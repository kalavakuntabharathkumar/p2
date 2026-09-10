from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./fund_analytics.db"
    redis_url: str = "redis://localhost:6379/0"
    sentry_dsn: str = ""
    cache_ttl_seconds: int = 300
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
