from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PromoValidation:
    valid: bool
    reason: Optional[str] = None


def validate_promo_dates(
    starts_at: Optional[datetime],
    expires_at: Optional[datetime],
    now: datetime,
) -> PromoValidation:

    if starts_at and now < starts_at:
        return PromoValidation(
            valid=False,
            reason="Промокод ещё не активен.",
        )

    if expires_at and now > expires_at:
        return PromoValidation(
            valid=False,
            reason="Срок действия промокода закончился.",
        )

    return PromoValidation(valid=True)
