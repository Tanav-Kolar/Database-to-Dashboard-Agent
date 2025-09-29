# mcp-agent-system/mcp_server/utils/ollama_client.py

import requests
import sys
import os

# Adjust path to import from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import OLLAMA_MODEL, OLLAMA_BASE_URL

class OllamaClient:
    """A client for interacting with the Ollama API, compatible with agno."""

    def __init__(self, model: str = OLLAMA_MODEL, host: str = OLLAMA_BASE_URL):
        self.model = model
        self.host = host

    def __call__(self, messages: list[dict]) -> str:
        """
        Makes a call to the Ollama API's generate endpoint.

        Args:
            messages: A list of message dictionaries, following the agno format.

        Returns:
            The text response from the model.
        """
        # For Ollama's /api/generate, we format the history into a single prompt string.
        # The final message is the most important one for the immediate task.
        prompt = messages[-1]['content']

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.RequestException as e:
            error_message = f"Error calling Ollama API: {e}"
            print(error_message)
            return error_message