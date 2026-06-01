import logging
import json
from typing import AsyncGenerator, Optional

import httpx

from ai.providers.base import AIProvider

logger = logging.getLogger(__name__)


class CustomAPIProvider(AIProvider):
    """Custom API provider for external LLM services."""
    
    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.3,
    ):
        super().__init__(base_url=api_url, model=model, temperature=temperature)
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate response using custom API."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = await self.client.post(
                self.base_url,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "stream": True,
                },
            )
            
            if response.status_code != 200:
                yield f"Error: API returned {response.status_code}"
                return
            
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        if 'choices' in data:
                            for choice in data['choices']:
                                if 'delta' in choice and 'content' in choice['delta']:
                                    yield choice['delta']['content']
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Custom API error: {e}")
            yield f"Error: {str(e)}"
    
    async def is_available(self) -> bool:
        """Check if custom API is available."""
        try:
            response = await self.client.get(self.base_url, timeout=5.0)
            return response.status_code < 500
        except Exception:
            return False
    
    async def close(self):
        await self.client.aclose()