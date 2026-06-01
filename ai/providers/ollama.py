import logging
import json
from typing import AsyncGenerator, Optional

import httpx

from ai.providers.base import AIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """Ollama local LLM provider."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:3b",
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ):
        super().__init__(base_url, model, temperature)
        self.max_tokens = max_tokens
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(self, prompt: str, system: str = None) -> AsyncGenerator[str, None]:
        """Generate a response using Ollama API with streaming."""
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "options": {
                        "temperature": self.temperature,
                    }
                },
            ) as response:
                if response.status_code != 200:
                    logger.error(f"Ollama returned status {response.status_code}")
                    yield f"Error: Ollama service returned status {response.status_code}"
                    return
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama")
            yield "Error: Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434"
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            yield f"Error: {str(e)}"
    
    async def stream(self, prompt: str, system: str = None) -> AsyncGenerator[str, None]:
        """Stream a response - alias for generate()."""
        async for chunk in self.generate(prompt, system):
            yield chunk
    
    async def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def health_check(self) -> bool:
        """Check if provider is healthy and model is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                return False
            
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            return self.model in models
        except Exception:
            return False
    
    async def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m['name'] for m in data.get('models', [])]
            return []
        except Exception:
            return []
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()