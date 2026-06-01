"""
AI Provider Router - Smart routing between different LLM providers
Falls back to cloud providers if local Ollama fails
"""
import logging
from typing import Optional, Dict, Any
from backend.config import get_settings
from backend.services.cache import cache

logger = logging.getLogger(__name__)
settings = get_settings()


class AIRouter:
    """Routes AI requests to appropriate provider with fallback support."""
    
    def __init__(self):
        self.current_provider = settings.ai_provider
        self.fallback_enabled = settings.ai_fallback_enabled
        self.providers = ["ollama", "openai", "anthropic"]
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate response using best available provider.
        Automatically falls back if primary fails.
        """
        if not temperature:
            temperature = settings.ollama_temperature
        if not max_tokens:
            max_tokens = settings.ollama_max_tokens
        
        # Try primary provider first
        try:
            return await self._call_provider(
                self.current_provider, 
                prompt, 
                system_prompt,
                temperature,
                max_tokens,
                context
            )
        except Exception as e:
            logger.warning(f"Primary provider {self.current_provider} failed: {e}")
            
            # Try fallback providers
            if self.fallback_enabled:
                for provider in self.providers:
                    if provider != self.current_provider:
                        try:
                            logger.info(f"Falling back to {provider}")
                            return await self._call_provider(
                                provider, 
                                prompt, 
                                system_prompt,
                                temperature,
                                max_tokens,
                                context
                            )
                        except Exception as fallback_error:
                            logger.warning(f"Fallback {provider} also failed: {fallback_error}")
                            continue
            
            # If all providers fail, return error message
            return "AI services are currently unavailable. Please try again later."
    
    async def _call_provider(
        self, 
        provider: str, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        context: Dict[str, Any] = None
    ) -> str:
        """Call specific provider."""
        if provider == "ollama":
            return await self._call_ollama(prompt, system_prompt, temperature, max_tokens)
        elif provider == "openai":
            return await self._call_openai(prompt, system_prompt, temperature, max_tokens)
        elif provider == "anthropic":
            return await self._call_anthropic(prompt, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _call_ollama(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Call Ollama local API."""
        import aiohttp
        
        url = f"{settings.ollama_base_url}/api/generate"
        
        payload = {
            "model": settings.ollama_model,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "temperature": temperature or settings.ollama_temperature,
            "options": {
                "num_predict": max_tokens or settings.ollama_max_tokens
            },
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=payload, 
                timeout=aiohttp.ClientTimeout(total=settings.ollama_timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "").strip()
                else:
                    raise Exception(f"Ollama error: {response.status}")
    
    async def _call_openai(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Call OpenAI API."""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        import aiohttp
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": settings.openai_model,
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 1024
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=payload, 
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    raise Exception(f"OpenAI error: {response.status} - {error}")
    
    async def _call_anthropic(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None
    ) -> str:
        """Call Anthropic Claude API."""
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        import aiohttp
        
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.anthropic_model,
            "max_tokens": max_tokens or 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        if temperature:
            payload["temperature"] = temperature
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=payload, 
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["content"][0]["text"]
                else:
                    error = await response.text()
                    raise Exception(f"Anthropic error: {response.status} - {error}")


# Global router instance
ai_router = AIRouter()