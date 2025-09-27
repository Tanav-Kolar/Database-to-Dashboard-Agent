#config.py
import os

# --- Database Configuration ---
DB_CONFIG = {
    "user": os.environ.get("DB_USER", "your_username"),
    "password": os.environ.get("DB_PASSWORD", "your_password"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "your_database")
}

# --- LLM Configuration ---
# Specify the Ollama model you want to use.
# Make sure you have pulled this model using `ollama pull <model_name>`
OLLAMA_MODEL = "llama3"  

# Specify the base URL for the Ollama server.
OLLAMA_BASE_URL = "http://localhost:11434"

# --- Server Configuration ---
API_HOST = "0.0.0.0"
API_PORT = 8000
