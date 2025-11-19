import os
import logging
from typing import Optional, Dict, Any
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("ollama-client")

class OllamaClient:
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        
        # Configure client if needed (ollama python lib uses env vars or defaults)
        # If host is different from default, we might need to set OLLAMA_HOST env var
        if self.host:
            os.environ["OLLAMA_HOST"] = self.host

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            logger.error(f"Failed to generate response from Ollama: {e}")
            raise

    def check_connection(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            ollama.list()
            return True
        except Exception:
            return False
