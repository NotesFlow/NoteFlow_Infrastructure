import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "NoteFlow Auth Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    AUTH_SERVICE_PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8001"))

    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "127.0.0.1")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5433")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "noteflow")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "noteflow_user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "noteflow_pass")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_this_in_real_env")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


settings = Settings()
