import logging
from typing import AsyncGenerator, Optional

from ai.providers.base import AIProvider

logger = logging.getLogger(__name__)


class LocalGGUFProvider(AIProvider):
    """Local GGUF model provider (placeholder for llama.cpp bindings)."""
    
    def __init__(
        self,
        model_path: str,
        temperature: float = 0.3,
    ):
        super().__init__(model=model_path, temperature=temperature)
        self.model_path = model_path
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate response from local GGUF model."""
        yield "Note: Local GGUF support requires llama.cpp Python bindings. "
        yield "Please use Ollama provider for local inference."
    
    async def is_available(self) -> bool:
        """Check if local model is available."""
        return False
    
    async def close(self):
        pass