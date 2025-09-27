import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# This adjusts the Python path to allow importing from the root directory.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from config import DB_CONFIG

# Construct the database connection URL from our configuration settings.
# SQLAlchemy uses this specific format: "postgresql+psycopg2://user:password@host:port/dbname"
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

def create_db_engine() -> Engine | None:
    """
    Creates and returns a SQLAlchemy engine instance.
    It gracefully handles connection errors and prints a helpful message.
    """
    try:
        # Create the engine. The engine manages a pool of database connection for efficiency, rather than creating a new connection for every query.
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            print("Successfully connected to the PostgreSQL database.")
        
        return engine
    except SQLAlchemyError as e:
        # Catch any database-related errors (e.g., wrong password, server down).
        print(f"An error occurred while connecting to the database: {e}")
        print("-> Please check your .env file and ensure the database server is running.")
        return None

# Create a single, shared engine instance. Other parts of the codebase will use this when needed.
engine = create_db_engine()
