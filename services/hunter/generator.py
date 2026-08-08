from itertools import product

from services.hunter.beauty import (
    is_beautiful,
)
from services.hunter.dictionary import (
    dictionary_candidates,
)
from services.hunter.ranker import (
    rank_usernames,
)


VOWELS = "aeiou"

CONSONANTS = (
    "bcdfghjklmnprstvwyz"
)

SYLLABLES = [
    "va", "ve", "vi", "vo",
    "la", "le", "li", "lo",
    "na", "ne", "ni", "no",
    "ra", "re", "ri", "ro",
    "sa", "se", "si", "so",
    "ma", "me", "mi", "mo",
    "ta", "te", "ti", "to",
    "ka", "ke", "ki", "ko",
    "za", "ze", "zi", "zo",
]

BRAND_BASES = [
    "nova",
    "luna",
    "vela",
    "vera",
    "nexa",
    "zora",
    "riva",
    "mira",
    "sora",
    "nora",
    "aura",
    "nexo",
    "nero",
    "avero",
    "velor",
    "valor",
    "prime",
    "royal",
    "elite",
    "orbit",
    "pixel",
    "vision",
]


def generate_pattern(
    length: int,
) -> list[str]:

    patterns = []

    if length == 5:
        patterns = [
            "CVCVC",
            "CVCCV",
            "VCVCV",
        ]

    elif length == 6:
        patterns = [
            "CVCVCV",
            "CVCCVC",
            "CVCVCC",
            "VCVCVC",
        ]

    elif length == 7:
        patterns = [
            "CVCVCVC",
            "CVCCVCV",
        ]

    else:
        return []

    result = set()

    for pattern in patterns:

        pools = []

        for char in pattern:

            if char == "C":
                pools.append(CONSONANTS)
            else:
                pools.append(VOWELS)

        for combination in product(*pools):

            username = "".join(
                combination
            )

            if is_beautiful(username):
                result.add(username)

    return list(result)


def generate_syllable_candidates(
    length: int,
) -> list[str]:

    result = set()

    for first in SYLLABLES:

        for second in SYLLABLES:

            candidate = (
                first + second
            )

            if len(candidate) == length:
                if is_beautiful(candidate):
                    result.add(candidate)

    return list(result)


def generate_brand_candidates(
    length: int,
) -> list[str]:

    result = set()

    for base in BRAND_BASES:

        if len(base) == length:
            result.add(base)

        if len(base) < length:

            suffixes = [
                "a",
                "o",
                "x",
                "y",
                "io",
                "ai",
            ]

            for suffix in suffixes:

                candidate = (
                    base + suffix
                )

                if len(candidate) == length:
                    if is_beautiful(candidate):
                        result.add(candidate)

    return list(result)


def generate_candidates(
    length: int,
    limit: int = 5000,
) -> list[str]:

    candidates = set()

    candidates.update(
        dictionary_candidates(length)
    )

    candidates.update(
        generate_brand_candidates(length)
    )

    candidates.update(
        generate_syllable_candidates(length)
    )

    candidates.update(
        generate_pattern(length)
    )

    beautiful = [
        username
        for username in candidates
        if is_beautiful(username)
    ]

    ranked = rank_usernames(
        beautiful
    )

    return ranked[:limit]
