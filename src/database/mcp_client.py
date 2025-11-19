import asyncio
import os
import sys
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        # Get the path to the server script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_script = os.path.join(current_dir, "postgres_mcp_server.py")
        self.session: Optional[ClientSession] = None
        self._exit_stack = None

    @asynccontextmanager
    async def connect(self):
        """Establish connection to the MCP server."""
        # Define server parameters
        server_params = StdioServerParameters(
            command=sys.executable,  # Use the same Python interpreter
            args=[self.server_script],
            env=os.environ.copy()  # Pass current environment (including DB credentials)
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()
                yield self

    async def list_tables(self) -> List[str]:
        """List all tables in the database."""
        if not self.session:
            raise RuntimeError("Client not connected")
        
        result = await self.session.call_tool("list_tables", arguments={})
        if result.content and result.content[0].type == "text":
             text = result.content[0].text
             # print(f"DEBUG: Raw list_tables response: {text!r}")
             import json
             try:
                 data = json.loads(text)
                 if isinstance(data, list):
                     return data
                 return [str(data)]
             except json.JSONDecodeError:
                 # If not JSON, maybe it's a raw string representation or just the string
                 if text.startswith("[") and text.endswith("]"):
                     try:
                         import ast
                         return ast.literal_eval(text)
                     except:
                         pass
                 return [text] if text else []
        return []

    async def get_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema for a table."""
        if not self.session:
            raise RuntimeError("Client not connected")
        
        result = await self.session.call_tool("get_schema", arguments={"table_name": table_name})
        if result.content and result.content[0].type == "text":
             text = result.content[0].text
             import json
             try:
                 data = json.loads(text)
                 if isinstance(data, list):
                     return data
                 return [data]
             except json.JSONDecodeError:
                 return []
        return []

    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query."""
        if not self.session:
            raise RuntimeError("Client not connected")
        
        result = await self.session.call_tool("execute_query", arguments={"query": query})
        if result.content and result.content[0].type == "text":
             text = result.content[0].text
             import json
             try:
                 data = json.loads(text)
                 if isinstance(data, list):
                     return data
                 return [data]
             except json.JSONDecodeError:
                 return []
        return []

# Example usage
async def main():
    client = MCPClient()
    try:
        async with client.connect() as mcp:
            print("Connected to MCP Server")
            
            tables = await mcp.list_tables()
            print(f"Tables: {tables}")
            
            if tables:
                schema = await mcp.get_schema(tables[0])
                print(f"Schema for {tables[0]}: {schema}")
                
                # Test query
                results = await mcp.execute_query(f"SELECT * FROM {tables[0]} LIMIT 5")
                print(f"Sample data: {results}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
