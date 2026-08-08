import re


BAD_PATTERNS = [
    "qz",
    "zq",
    "qx",
    "xq",
    "qj",
    "jq",
    "zx",
    "xz",
    "qw",
    "wq",
    "vj",
    "jv",
    "xv",
    "vx",
    "zv",
    "vz",
]

REPEATED_BAD = re.compile(
    r"(.)\1\1"
)


def has_bad_pattern(username: str) -> bool:
    username = username.lower()

    for pattern in BAD_PATTERNS:
        if pattern in username:
            return True

    return False


def has_excessive_repetition(username: str) -> bool:
    return bool(
        REPEATED_BAD.search(username)
    )


def vowel_ratio(username: str) -> float:
    if not username:
        return 0.0

    vowels = sum(
        1
        for char in username
        if char in "aeiou"
    )

    return vowels / len(username)


def has_reasonable_structure(username: str) -> bool:
    ratio = vowel_ratio(username)

    return 0.20 <= ratio <= 0.70


def is_beautiful_candidate(username: str) -> bool:
    if has_bad_pattern(username):
        return False

    if has_excessive_repetition(username):
        return False

    if not has_reasonable_structure(username):
        return False

    return True
