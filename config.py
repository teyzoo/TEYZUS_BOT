from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram Bot
    bot_token: str = Field(alias="BOT_TOKEN")

    # Database
    database_url: str = Field(alias="DATABASE_URL")

    # Owner
    owner_id: int = Field(alias="OWNER_ID")

    # Telegram API for username checking
    telegram_api_id: int = Field(alias="TELEGRAM_API_ID")
    telegram_api_hash: str = Field(alias="TELEGRAM_API_HASH")

    # Bot
    bot_name: str = Field(
        default="TEYZUS",
        alias="BOT_NAME",
    )

    bot_username: str = Field(
        default="TEYZUS_Bot",
        alias="BOT_USERNAME",
    )

    # Web
    web_host: str = Field(
        default="0.0.0.0",
        alias="WEB_HOST",
    )

    web_port: int = Field(
        default=10000,
        alias="WEB_PORT",
    )

    # Search
    free_search_length: int = Field(
        default=6,
        alias="FREE_SEARCH_LENGTH",
    )

    premium_search_length: int = Field(
        default=5,
        alias="PREMIUM_SEARCH_LENGTH",
    )

    free_daily_limit: int = Field(
        default=5,
        alias="FREE_DAILY_LIMIT",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
