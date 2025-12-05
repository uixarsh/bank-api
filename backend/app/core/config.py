import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.envs/.env.local"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"
    )

    PROJECT_NAME: str = ""
    PROJECT_DESCRIPTION: str = ""
    PROJECT_VERSION: str = ""
    API_V1_STR: str = ""
    SITE_NAME: str = ""
    

settings = Settings()