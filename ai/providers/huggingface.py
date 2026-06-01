import logging
from typing import AsyncGenerator, Optional

import httpx

from ai.providers.base import AIProvider

logger = logging.getLogger(__name__)


class HuggingFaceProvider(AIProvider):
    """HuggingFace inference API provider."""
    
    def __init__(
        self,
        api_token: str,
        model: str = "meta-llama/Llama-2-7b-chat-hf",
        temperature: float = 0.3,
    ):
        super().__init__(model=model, temperature=temperature)
        self.api_token = api_token
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate response using HuggingFace API."""
        try:
            response = await self.client.post(
                f"https://api-inference.huggingface.co/models/{self.model}",
                headers={"Authorization": f"Bearer {self.api_token}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "temperature": self.temperature,
                        "max_new_tokens": 500,
                    }
                },
            )
            
            if response.status_code != 200:
                yield f"Error: HuggingFace API returned {response.status_code}"
                return
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                yield data[0].get('generated_text', '')[len(prompt):]
            else:
                yield str(data)
        except Exception as e:
            logger.error(f"HuggingFace error: {e}")
            yield f"Error: {str(e)}"
    
    async def is_available(self) -> bool:
        """Check if HuggingFace API is available."""
        try:
            response = await self.client.head(
                f"https://api-inference.huggingface.co/models/{self.model}",
                headers={"Authorization": f"Bearer {self.api_token}"},
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        await self.client.aclose()