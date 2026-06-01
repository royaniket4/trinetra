import logging
from typing import Optional, Dict, Any

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_providers: Dict[str, Any] = {}


def get_provider(name: str = None) -> Any:
    """Get AI provider instance based on configuration."""
    global _providers
    
    provider_name = name or settings.ai_provider
    
    if provider_name in _providers:
        return _providers[provider_name]
    
    from ai.providers.ollama import OllamaProvider
    from ai.providers.huggingface import HuggingFaceProvider
    from ai.providers.local_gguf import LocalGGUFProvider
    from ai.providers.custom_api import CustomAPIProvider
    
    provider = None
    
    if provider_name == "ollama":
        provider = OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.ollama_temperature,
            max_tokens=settings.ollama_max_tokens,
        )
    elif provider_name == "huggingface":
        if settings.huggingface_api_token:
            provider = HuggingFaceProvider(
                api_token=settings.huggingface_api_token,
                model=settings.huggingface_model or "meta-llama/Llama-2-7b-chat-hf",
                temperature=settings.ollama_temperature,
            )
        else:
            logger.warning("HuggingFace provider requested but no API token configured")
            provider = OllamaProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=settings.ollama_temperature,
            )
    elif provider_name == "local_gguf":
        provider = LocalGGUFProvider(
            model_path=settings.gguf_model_path,
            temperature=settings.ollama_temperature,
        )
    elif provider_name == "custom_api":
        provider = CustomAPIProvider(
            api_url=settings.custom_api_url,
            api_key=settings.custom_api_key,
            model=settings.custom_api_model or "gpt-4",
            temperature=settings.ollama_temperature,
        )
    else:
        logger.warning(f"Unknown AI provider: {provider_name}, falling back to Ollama")
        provider = OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.ollama_temperature,
        )
    
    _providers[provider_name] = provider
    return provider


def clear_providers() -> None:
    """Clear cached provider instances."""
    global _providers
    for provider in _providers.values():
        if hasattr(provider, 'close'):
            provider.close()
    _providers.clear()