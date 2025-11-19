import os
import json
import logging
from typing import Any, List, Dict, Optional
from contextlib import asynccontextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("postgres-mcp-server")

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("postgres-mcp-server")

def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def is_read_only(query: str) -> bool:
    """Check if a query is read-only."""
    forbidden_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", 
        "CREATE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK"
    ]
    normalized_query = query.strip().upper()
    
    # Check for forbidden keywords at the start or after a semicolon
    # This is a basic check; for production, use a proper SQL parser
    for keyword in forbidden_keywords:
        if normalized_query.startswith(keyword) or f"; {keyword}" in normalized_query or f";{keyword}" in normalized_query:
            return False
    return True

@mcp.tool()
def list_tables() -> List[str]:
    """List all tables in the public schema."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            return tables
    finally:
        conn.close()

@mcp.tool()
def get_schema(table_name: str) -> List[Dict[str, Any]]:
    """Get the schema for a specific table."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = %s
            """, (table_name,))
            schema = cur.fetchall()
            return [dict(row) for row in schema]
    finally:
        conn.close()

@mcp.tool()
def execute_query(query: str) -> List[Dict[str, Any]]:
    """Execute a read-only SQL query."""
    if not is_read_only(query):
        raise ValueError("Only read-only queries (SELECT) are allowed.")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            results = cur.fetchall()
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()
