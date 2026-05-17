from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "NoteFlow Notes Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    NOTES_SERVICE_HOST: str = "0.0.0.0"
    NOTES_SERVICE_PORT: int = 8002

    AUTH_SERVICE_URL: str = "http://127.0.0.1:8001"
    NOTES_DATA_SERVICE_URL: str = "http://127.0.0.1:8003"

    REQUEST_TIMEOUT_SECONDS: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
