from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./amazon.sqlite3"

    PROXY_URL: str | None = None

    BROWSER_HEADLESS: bool = True

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
