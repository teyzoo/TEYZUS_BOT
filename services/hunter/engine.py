import asyncio
from dataclasses import dataclass
from typing import Optional

from services.hunter.filters import (
    is_beautiful_candidate,
)
from services.hunter.generator import (
    generate_candidates,
)
from services.hunter.pricing import (
    estimate_price,
)
from services.hunter.scorer import (
    beauty_score,
    brand_score,
    liquidity_score,
    rarity_score,
    readability_score,
)
from services.hunter.telegram_checker import (
    TelegramChecker,
    TelegramUsernameStatus,
)
from services.hunter.tme_checker import (
    TMeChecker,
)


@dataclass
class HunterResult:
    username: str

    available: bool

    beauty_score: float
    readability: float
    rarity: float
    brand: float
    liquidity: float

    price_min: int
    price_max: int

    telegram_status: str
    tme_available: bool


class HunterEngine:

    def __init__(self) -> None:
        self.telegram = TelegramChecker()
        self.tme = TMeChecker()

    async def close(self) -> None:
        await self.telegram.close()

    def prepare_candidates(
        self,
        length: int,
        amount: int = 1000,
    ) -> list[str]:

        generated = generate_candidates(
            length=length,
            limit=amount * 10,
        )

        beautiful = [
            username
            for username in generated
            if is_beautiful_candidate(username)
        ]

        beautiful.sort(
            key=beauty_score,
            reverse=True,
        )

        return beautiful[:amount]

    async def check_candidate(
        self,
        username: str,
    ) -> Optional[HunterResult]:

        telegram_status = await self.telegram.check(
            username
        )

        if (
            telegram_status
            != TelegramUsernameStatus.AVAILABLE
        ):
            return None

        tme_available = await self.tme.check(
            username
        )

        if not tme_available:
            return None

        readability = readability_score(username)
        rarity = rarity_score(username)
        brand = brand_score(username)
        liquidity = liquidity_score(username)
        beauty = beauty_score(username)

        price_min, price_max = estimate_price(
            username
        )

        return HunterResult(
            username=username,
            available=True,
            beauty_score=beauty,
            readability=readability,
            rarity=rarity,
            brand=brand,
            liquidity=liquidity,
            price_min=price_min,
            price_max=price_max,
            telegram_status=telegram_status.value,
            tme_available=tme_available,
        )

    async def search(
        self,
        length: int,
        amount: int = 10,
    ) -> list[HunterResult]:

        candidates = self.prepare_candidates(
            length=length,
            amount=max(
                amount * 5,
                50,
            ),
        )

        results: list[HunterResult] = []

        for candidate in candidates:

            result = await self.check_candidate(
                candidate
            )

            if result is None:
                continue

            results.append(result)

            if len(results) >= amount:
                break

        results.sort(
            key=lambda item: (
                item.beauty_score,
                item.liquidity,
                item.price_max,
            ),
            reverse=True,
        )

        return results[:amount]
