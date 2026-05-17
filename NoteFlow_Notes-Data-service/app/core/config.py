import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "NoteFlow Notes Data Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    NOTES_DATA_SERVICE_HOST: str = os.getenv("NOTES_DATA_SERVICE_HOST", "0.0.0.0")
    NOTES_DATA_SERVICE_PORT: int = int(os.getenv("NOTES_DATA_SERVICE_PORT", "8003"))

    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "127.0.0.1")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5433")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "noteflow")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "noteflow_user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "noteflow_pass")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


settings = Settings()
