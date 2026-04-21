from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    livekit_url: str = "ws://localhost:7880"
    livekit_public_url: str = "ws://localhost:7880"
    livekit_api_key: str
    livekit_api_secret: str
    openai_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./db/local.db"


settings = Settings()
