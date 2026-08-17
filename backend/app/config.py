from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    tavily_api_key: str = ""

    default_model_provider: str = "openai"
    default_model_name: str = "gpt-4o"

    database_url: str = "sqlite+aiosqlite:///./data/platform.db"

    max_retries: int = 3
    retry_base_delay: float = 2.0

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
