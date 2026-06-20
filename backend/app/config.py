from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./pumpshield.db"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    notion_token: str = ""
    notion_database_id: str = ""

    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
