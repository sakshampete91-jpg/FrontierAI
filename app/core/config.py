from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration for CHOKO."""

    app_name: str = "CHOKO"
    app_version: str = "1.0.0"

    # AI provider
    ai_provider: str = "gemini"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # Local Ollama fallback
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()