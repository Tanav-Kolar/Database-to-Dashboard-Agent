# mcp-agent-system/tests/test_connection.py

import sys
import os

# --- Path Adjustment ---
# This is the key change. We are telling Python to add the parent directory
# (the project's root folder 'mcp-agent-system') to its list of paths to check for modules.
# os.path.dirname(__file__) gives us the current directory ('/tests').
# os.path.join(..., '..') goes up one level to the root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


print("Attempting to connect to the database...")

# When we import the 'engine' from our connector, it will execute the
# connection logic contained within db_connector.py.
try:
    from mcp_server.utils.db_connector import engine
    if engine is None:
        print("\nDatabase engine failed to initialize. Please check the error messages above.")
    else:
        print("\nTest script finished. Connection status was printed above.")
except ImportError as e:
    print(f"An error occurred during import: {e}")
