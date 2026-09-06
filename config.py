from __future__ import annotations

import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower().strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

ADMIN_IDS = {
    int(value.strip())
    for value in os.getenv("ADMIN_IDS", "").split(",")
    if value.strip().isdigit()
}

FREE_SEARCHES_PER_DAY = int(
    os.getenv("FREE_SEARCHES_PER_DAY", "5")
)

PREMIUM_SEARCHES_PER_DAY = int(
    os.getenv("PREMIUM_SEARCHES_PER_DAY", "1000")
)

FREE_MIN_USERNAME_LENGTH = int(
    os.getenv("FREE_MIN_USERNAME_LENGTH", "6")
)

PREMIUM_MIN_USERNAME_LENGTH = int(
    os.getenv("PREMIUM_MIN_USERNAME_LENGTH", "5")
)

MAX_USERNAME_LENGTH = int(
    os.getenv("MAX_USERNAME_LENGTH", "32")
)

PREMIUM_BATCH_SIZE = int(
    os.getenv("PREMIUM_BATCH_SIZE", "10")
)

TRAP_INTERVAL_SECONDS = int(
    os.getenv("TRAP_INTERVAL_SECONDS", "300")
)

SEARCH_TIMEOUT_SECONDS = float(
    os.getenv("SEARCH_TIMEOUT_SECONDS", "10")
)

PORT = int(
    os.getenv("PORT", "10000")
)

APP_NAME = os.getenv(
    "APP_NAME",
    "TEYZUS",
).strip()

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not configured"
    )
