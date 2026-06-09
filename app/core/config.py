from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "progridai-tools-api"
    VERSION: str = "1.0.0"
    API_KEY: str
    DATABASE_URL: str = "postgresql+asyncpg://postgres:Bravida%402023%21@localhost:5432/progridai"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
