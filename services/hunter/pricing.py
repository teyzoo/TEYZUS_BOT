from services.hunter.scorer import (
    beauty_score,
    brand_score,
    liquidity_score,
    rarity_score,
    readability_score,
)


def estimate_price(username: str) -> tuple[int, int]:
    beauty = beauty_score(username)
    rarity = rarity_score(username)
    brand = brand_score(username)
    liquidity = liquidity_score(username)
    readability = readability_score(username)

    score = (
        beauty * 0.30
        + rarity * 0.20
        + brand * 0.25
        + liquidity * 0.15
        + readability * 0.10
    )

    length = len(username)

    if length == 5:
        base = 800
    elif length == 6:
        base = 300
    elif length == 7:
        base = 150
    else:
        base = 70

    multiplier = max(
        0.5,
        score / 5.0,
    )

    minimum = int(
        base * multiplier
    )

    maximum = int(
        minimum * 1.6
    )

    return (
        minimum,
        max(maximum, minimum + 1),
    )
