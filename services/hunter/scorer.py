from services.hunter.filters import (
    has_bad_pattern,
    has_excessive_repetition,
    vowel_ratio,
)


VOWELS = set("aeiou")


def readability_score(username: str) -> float:
    if not username:
        return 0.0

    score = 10.0

    ratio = vowel_ratio(username)

    if ratio < 0.20:
        score -= 3.0

    elif ratio > 0.70:
        score -= 1.5

    if has_bad_pattern(username):
        score -= 4.0

    if has_excessive_repetition(username):
        score -= 2.0

    for index in range(len(username) - 1):
        if username[index] in VOWELS:
            continue

        if username[index + 1] in VOWELS:
            score += 0.05

    return max(
        0.0,
        min(10.0, score),
    )


def rarity_score(username: str) -> float:
    score = 5.0

    length = len(username)

    if length == 5:
        score += 3.0
    elif length == 6:
        score += 2.0
    elif length <= 8:
        score += 1.0

    unique = len(set(username))

    if unique == length:
        score += 1.0

    return max(
        0.0,
        min(10.0, score),
    )


def brand_score(username: str) -> float:
    score = 5.0

    brand_fragments = [
        "nova",
        "luna",
        "aura",
        "vela",
        "vera",
        "nexa",
        "prime",
        "royal",
        "elite",
        "crypto",
        "token",
        "pixel",
        "orbit",
        "valor",
        "vision",
    ]

    for fragment in brand_fragments:
        if fragment in username:
            score += 3.0
            break

    return max(
        0.0,
        min(10.0, score),
    )


def liquidity_score(username: str) -> float:
    score = 4.0

    length = len(username)

    if length == 5:
        score += 3.0
    elif length == 6:
        score += 2.5
    elif length == 7:
        score += 1.5
    elif length <= 9:
        score += 0.5

    if username.isalpha():
        score += 1.0

    if "_" not in username:
        score += 0.5

    return max(
        0.0,
        min(10.0, score),
    )


def beauty_score(username: str) -> float:
    readability = readability_score(username)
    rarity = rarity_score(username)
    brand = brand_score(username)
    liquidity = liquidity_score(username)

    score = (
        readability * 0.35
        + rarity * 0.20
        + brand * 0.20
        + liquidity * 0.25
    )

    return round(
        min(10.0, score),
        2,
    )
