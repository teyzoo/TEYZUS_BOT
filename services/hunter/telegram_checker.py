import asyncio
import logging
from enum import StrEnum

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)

from config import settings


logger = logging.getLogger("TEYZUS.telegram_checker")


class TelegramUsernameStatus(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    INVALID = "invalid"
    FLOOD_WAIT = "flood_wait"
    ERROR = "error"


class TelegramChecker:

    def __init__(self) -> None:
        self.client = TelegramClient(
            "teyzus_checker",
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )

        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if not self.client.is_connected():
            await self.client.connect()

    async def close(self) -> None:
        if self.client.is_connected():
            await self.client.disconnect()

    async def check(
        self,
        username: str,
    ) -> TelegramUsernameStatus:

        username = username.lstrip("@")

        async with self._lock:

            try:
                await self.connect()

                await self.client.get_entity(
                    username
                )

                return TelegramUsernameStatus.OCCUPIED

            except UsernameNotOccupiedError:
                return TelegramUsernameStatus.AVAILABLE

            except UsernameInvalidError:
                return TelegramUsernameStatus.INVALID

            except FloodWaitError as error:
                logger.warning(
                    "Telegram flood wait: %s seconds",
                    error.seconds,
                )

                return TelegramUsernameStatus.FLOOD_WAIT

            except Exception:
                logger.exception(
                    "Telegram checker error for @%s",
                    username,
                )

                return TelegramUsernameStatus.ERROR
