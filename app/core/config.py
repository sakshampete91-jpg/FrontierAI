from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Application configuration for FrontierAI."""

    app_name: str = "FrontierAI"
    app_version: str = "1.0.0"

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    # Runtime
    environment: str = "local"
    log_level: str = "INFO"

    # Current local fallback used by the startup script.
    ollama_llm_library: str = "cpu_avx2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()