import math
import re


VOWELS = set("aeiou")

BAD_CLUSTERS = {
    "qz", "zq", "qx", "xq",
    "qj", "jq", "zx", "xz",
    "qw", "wq", "vj", "jv",
    "xv", "vx", "zv", "vz",
}

GOOD_CLUSTERS = {
    "ai", "au", "ea", "ee", "ei", "ia",
    "ie", "io", "oa", "oe", "oi", "ou",
    "va", "ve", "vi", "vo",
    "la", "le", "li", "lo",
    "na", "ne", "ni", "no",
    "ra", "re", "ri", "ro",
    "sa", "se", "si", "so",
    "ma", "me", "mi", "mo",
    "ta", "te", "ti", "to",
}


def vowel_ratio(username: str) -> float:
    if not username:
        return 0.0

    letters = [
        char for char in username
        if char.isalpha()
    ]

    if not letters:
        return 0.0

    return sum(
        char in VOWELS
        for char in letters
    ) / len(letters)


def alternating_score(username: str) -> float:
    if len(username) < 2:
        return 0.0

    transitions = 0

    for first, second in zip(
        username,
        username[1:],
    ):
        if (
            (first in VOWELS)
            != (second in VOWELS)
        ):
            transitions += 1

    return transitions / (len(username) - 1)


def bad_cluster_score(username: str) -> float:
    penalty = 0.0

    for index in range(len(username) - 1):
        pair = username[index:index + 2]

        if pair in BAD_CLUSTERS:
            penalty += 2.0

    return penalty


def good_cluster_bonus(username: str) -> float:
    bonus = 0.0

    for index in range(len(username) - 1):
        pair = username[index:index + 2]

        if pair in GOOD_CLUSTERS:
            bonus += 0.25

    return min(2.0, bonus)


def repetition_penalty(username: str) -> float:
    penalty = 0.0

    if re.search(r"(.)\1\1", username):
        penalty += 2.5

    if re.search(r"(.)\1", username):
        penalty += 0.5

    return penalty


def digit_penalty(username: str) -> float:
    digits = sum(
        char.isdigit()
        for char in username
    )

    return min(
        3.0,
        digits * 0.75,
    )


def underscore_penalty(username: str) -> float:
    return username.count("_") * 1.5


def length_score(username: str) -> float:
    length = len(username)

    if length == 5:
        return 10.0

    if length == 6:
        return 9.5

    if length == 7:
        return 8.5

    if length == 8:
        return 7.5

    if length == 9:
        return 6.5

    if length <= 12:
        return 5.0

    return 3.0


def readability_score(username: str) -> float:
    if not username:
        return 0.0

    score = 5.0

    ratio = vowel_ratio(username)

    if 0.30 <= ratio <= 0.60:
        score += 2.0
    elif 0.20 <= ratio <= 0.70:
        score += 1.0
    else:
        score -= 1.5

    score += alternating_score(username) * 1.5

    score += good_cluster_bonus(username)

    score -= bad_cluster_score(username)
    score -= repetition_penalty(username)
    score -= digit_penalty(username)
    score -= underscore_penalty(username)

    return round(
        max(0.0, min(10.0, score)),
        2,
    )


def beauty_score(username: str) -> float:
    readability = readability_score(username)
    length = length_score(username)

    score = (
        readability * 0.70
        + length * 0.30
    )

    return round(
        max(0.0, min(10.0, score)),
        2,
    )


def is_beautiful(username: str) -> bool:
    username = username.lower()

    if not re.fullmatch(
        r"[a-z0-9_]+",
        username,
    ):
        return False

    if len(username) < 5:
        return False

    if username.startswith("_"):
        return False

    if username.endswith("_"):
        return False

    if bad_cluster_score(username) >= 2:
        return False

    if repetition_penalty(username) >= 2.5:
        return False

    if readability_score(username) < 6.0:
        return False

    return True
