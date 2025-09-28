#sql_tools.py
import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
import sys
import os

# Adjust path to import from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_server.utils.readonly_validator import ReadOnlyValidator
from mcp_server.utils.db_connector import engine as db_engine

class SqlReadOnlyTool:
    """
    A tool for safely querying a SQL database in a read-only manner.
    It provides methods to get the database schema and execute validated
    SELECT queries.
    """

    def __init__(self, engine: Engine):
        """
        Initializes the tool with a SQLAlchemy database engine.

        Args:
            engine: A SQLAlchemy Engine instance connected to the target database.
        """
        if engine is None:
            raise ValueError("Database engine cannot be None.")
        self.engine = engine
        self.inspector = inspect(self.engine)

    def get_schema_representation(self) -> str:
        """
        Retrieves a string representation of the database schema.
        This helps the LLM understand the available tables and columns.

        Returns:
            A string detailing the tables and their columns.
        """
        schema_info = []
        tables = self.inspector.get_table_names()
        for table_name in tables:
            columns = self.inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            schema_info.append(f"Table '{table_name}' has columns: {', '.join(column_names)}")
        
        return "\n".join(schema_info)

    def execute_query(self, sql_query: str) -> pd.DataFrame | str:
        """
        Executes a SQL query after validating that it is read-only.

        Args:
            sql_query: The SQL query to execute.

        Returns:
            A pandas DataFrame with the query results if successful and safe,
            or an error message string if the query is invalid or unsafe.
        """
        #Validate the query
        if not ReadOnlyValidator.is_readonly(sql_query):
            return "Error: Query is not read-only. Only SELECT statements are allowed."

        #Execute the query
        try:
            with self.engine.connect() as connection:
                # We use pandas to easily read SQL results into a DataFrame
                df = pd.read_sql_query(text(sql_query), connection)
                return df
        except Exception as e:
            # Catch potential SQL syntax errors or other database issues
            return f"An error occurred while executing the query: {e}"

# We can create a default instance of the tool to be easily imported elsewhere
sql_tool = SqlReadOnlyTool(engine=db_engine)
