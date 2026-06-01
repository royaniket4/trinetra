from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    app_name: str = "Trinetra"
    app_version: str = "1.0.0"
    
    # Database
    database_url: str = "sqlite:///./trinetra.db"
    db_pool_size: int = 20
    db_max_overflow: int = 40
    
    # API
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # WebSocket
    ws_endpoint: str = "/ws"
    
    # AI Provider
    ai_provider: str = "ollama"
    ai_fallback_enabled: bool = True
    
    # AI - Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_temperature: float = 0.3
    ollama_max_tokens: int = 1024
    ollama_timeout: int = 120
    
    # AI - OpenAI (Fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.3
    
    # AI - Anthropic Claude (Fallback)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # AI - HuggingFace
    huggingface_api_token: str = ""
    huggingface_model: str = "meta-llama/Llama-2-7b-chat-hf"
    
    # AI - Custom API
    custom_api_url: str = ""
    custom_api_key: str = ""
    custom_api_model: str = "gpt-4"
    
    # Redis Cache (Optional - for production)
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    
    # Synthetic Attack Generator
    simulator_enabled: bool = True
    simulator_interval_min: int = 5
    simulator_interval_max: int = 30
    
    # SOAR
    auto_response_enabled: bool = False
    auto_response_severity_threshold: int = 5
    
    # Stats
    stats_cache_ttl: int = 5
    
    # Auth - Security
    jwt_secret: str = "trinetra-dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # or "text"
    
    # Security Headers
    security_headers_enabled: bool = True
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def validate_security_settings():
    """Validate critical security settings."""
    settings = get_settings()
    
    # Check for default JWT secret
    if settings.jwt_secret == "trinetra-dev-secret-change-in-production":
        print("WARNING: Using default JWT secret! Set JWT_SECRET in .env")
    
    # Check for default CORS origins in production
    if "localhost" in str(settings.cors_origins) and os.getenv("ENVIRONMENT") == "production":
        print("WARNING: CORS allows localhost in production!")