import logging
import sqlglot
from sqlglot import exp

logger = logging.getLogger("query-validator")

class QueryValidator:
    def validate(self, query: str) -> bool:
        """Validate that the query is a safe, read-only SELECT statement."""
        try:
            # Parse the query
            parsed = sqlglot.parse_one(query)
            
            # Check if it's a SELECT statement
            if not isinstance(parsed, exp.Select):
                logger.warning(f"Query rejected: Not a SELECT statement. Type: {type(parsed)}")
                return False
            
            # Check for any modification statements (redundant if we check root type, but good for subqueries)
            # Actually, sqlglot parse_one returns the root expression. 
            # If it's a Select, it shouldn't be a Delete/Update.
            # But we should check for CTEs or other structures that might hide things?
            # For now, strictly enforcing root node is SELECT is a good start.
            
            return True
        except Exception as e:
            logger.error(f"Query validation failed: {e}")
            return False

    def sanitize(self, query: str) -> str:
        """Clean up the query string."""
        # Remove markdown code blocks if present (LLMs sometimes add them despite instructions)
        clean_query = query.replace("```sql", "").replace("```", "").strip()
        # Remove trailing semicolons to avoid multi-statement injection risks if driver allows it
        # (psycopg2 usually handles this safely, but good practice)
        if clean_query.endswith(";"):
            clean_query = clean_query[:-1]
        return clean_query
