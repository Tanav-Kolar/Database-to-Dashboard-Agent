# mcp-agent-system/mcp_server/tools/sql_readonly_tool.py

import sys
import os
import pandas as pd
from sqlalchemy import create_engine, inspect
from agno.tools import tool

# Adjust path to import from the root directory and other project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import DB_CONFIG
from mcp_server.utils.readonly_validator import ReadOnlyValidator

class SqlReadOnlyTool(tool):
    """A tool for safely querying a PostgreSQL database."""
    name = "SqlDatabaseReader"
    description = (
        "A tool that can execute a read-only SQL query on a PostgreSQL database and "
        "also describe the database's schema. IMPORTANT: It can only execute SELECT statements."
    )

    def __init__(self):
        super().__init__()
        self.db_uri = (
            f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        )
        try:
            self.engine = create_engine(self.db_uri)
            self.inspector = inspect(self.engine)
            print("Successfully connected to the database for SqlReadOnlyTool.")
        except Exception as e:
            print(f"Error connecting to database for SqlReadOnlyTool: {e}")
            self.engine = None
            self.inspector = None

    def get_schema_representation(self) -> str:
        """Returns a string representation of the database schema."""
        if not self.inspector:
            return "Error: Database connection not established."
        
        tables = self.inspector.get_table_names()
        schema_str = ""
        for table in tables:
            schema_str += f"Table '{table}' with columns:\n"
            columns = self.inspector.get_columns(table)
            for col in columns:
                schema_str += f"  - {col['name']} ({col['type']})\n"
        return schema_str

    def __call__(self, action: str, sql_query: str = "") -> str:
        """
        Executes a specified action.
        
        Args:
            action (str): The action to perform. Must be 'get_schema' or 'execute_query'.
            sql_query (str): The SQL query to execute (required if action is 'execute_query').
            
        Returns:
            A string containing the result (data as JSON, schema, or an error message).
        """
        if action == "get_schema":
            return self.get_schema_representation()
        
        elif action == "execute_query":
            if not ReadOnlyValidator.is_readonly(sql_query):
                return "Error: The provided query is not read-only. Only SELECT statements are allowed."
            try:
                with self.engine.connect() as connection:
                    df = pd.read_sql_query(sql_query, connection)
                    return df.to_json(orient='records')
            except Exception as e:
                return f"Error executing query: {e}"
        else:
            return "Error: Invalid action. Must be 'get_schema' or 'execute_query'."

# Instantiate the tool for easy import
sql_tool = SqlReadOnlyTool()
