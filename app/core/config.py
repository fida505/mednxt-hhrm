from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./mednxt_hhrm.db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mednxt-hhrm-secret-key-2024")
    DEFAULT_TENANT_ID: str = "00000000-0000-0000-0000-000000000001"
    PROJECT_NAME: str = "MedNXT HHRM"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
