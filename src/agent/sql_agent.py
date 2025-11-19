import logging
import asyncio
from typing import Dict, Any, List, Optional

from src.database.mcp_client import MCPClient
from src.llm.ollama_client import OllamaClient
from src.llm.prompts import SQL_SYSTEM_PROMPT, SQL_GENERATION_TEMPLATE, ERROR_CORRECTION_TEMPLATE
from src.agent.query_validator import QueryValidator

logger = logging.getLogger("sql-agent")

class SQLAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        self.llm_client = OllamaClient()
        self.validator = QueryValidator()

    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a natural language query and return the results.
        """
        async with self.mcp_client.connect() as mcp:
            # 1. Fetch Schema Context
            try:
                tables = await mcp.list_tables()
                schema_context = ""
                for table in tables:
                    schema = await mcp.get_schema(table)
                    schema_context += f"Table: {table}\nColumns: {schema}\n\n"
            except Exception as e:
                logger.error(f"Failed to fetch schema: {e}")
                return {"error": "Failed to retrieve database schema."}

            # 2. Generate SQL
            prompt = SQL_GENERATION_TEMPLATE.format(
                schema_context=schema_context,
                user_query=user_query
            )
            
            try:
                generated_sql = self.llm_client.generate_response(prompt, system_prompt=SQL_SYSTEM_PROMPT)
                cleaned_sql = self.validator.sanitize(generated_sql)
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return {"error": "Failed to generate SQL query."}

            # 3. Validate SQL
            if not self.validator.validate(cleaned_sql):
                return {"error": "Generated SQL was invalid or unsafe.", "sql": cleaned_sql}

            # 4. Execute SQL
            try:
                results = await mcp.execute_query(cleaned_sql)
                return {
                    "success": True,
                    "sql": cleaned_sql,
                    "results": results,
                    "columns": list(results[0].keys()) if results else []
                }
            except Exception as e:
                # Optional: Implement retry with error correction here
                logger.error(f"Query execution failed: {e}")
                return {"error": f"Database error: {str(e)}", "sql": cleaned_sql}
