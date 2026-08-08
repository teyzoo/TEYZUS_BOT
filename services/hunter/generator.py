from itertools import product
import re


VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnprstvwyz"

COMMON_SYLLABLES = [
    "va",
    "ve",
    "vi",
    "vo",
    "vu",
    "la",
    "le",
    "li",
    "lo",
    "lu",
    "na",
    "ne",
    "ni",
    "no",
    "nu",
    "ra",
    "re",
    "ri",
    "ro",
    "ru",
    "sa",
    "se",
    "si",
    "so",
    "su",
    "za",
    "ze",
    "zi",
    "zo",
    "zu",
    "ma",
    "me",
    "mi",
    "mo",
    "mu",
    "ka",
    "ke",
    "ki",
    "ko",
    "ku",
    "ta",
    "te",
    "ti",
    "to",
    "tu",
]

BRAND_BASES = [
    "nova",
    "luna",
    "vela",
    "vera",
    "nexa",
    "vexa",
    "zora",
    "riva",
    "mira",
    "sora",
    "nora",
    "lora",
    "vivo",
    "aura",
    "zen",
    "zeno",
    "nero",
    "nexo",
    "avero",
    "velor",
    "monet",
    "valor",
    "vertex",
    "orbit",
    "pixel",
    "crypto",
    "token",
    "prime",
    "royal",
    "elite",
]

DICTIONARY_BASES = [
    "aura",
    "nova",
    "luna",
    "solar",
    "orbit",
    "prime",
    "royal",
    "pixel",
    "moneta",
    "valor",
    "vector",
    "vertex",
    "vision",
    "future",
    "legend",
    "crypto",
    "market",
    "studio",
    "design",
    "digital",
]


def normalize_username(value: str) -> str:
    value = value.lower().strip()
    value = value.replace("@", "")
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value


def is_valid_username(value: str) -> bool:
    if not 5 <= len(value) <= 32:
        return False

    if not re.fullmatch(r"[a-z0-9_]+", value):
        return False

    return True


def generate_syllable_candidates(
    length: int,
    limit: int = 5000,
) -> list[str]:

    result: set[str] = set()

    if length < 5:
        return []

    for first in COMMON_SYLLABLES:
        if len(first) >= length:
            candidate = first[:length]
            result.add(candidate)

        for second in COMMON_SYLLABLES:
            candidate = first + second

            if len(candidate) == length:
                result.add(candidate)

            if len(result) >= limit:
                return sorted(result)

    return sorted(result)


def generate_vowel_pattern_candidates(
    length: int,
    limit: int = 5000,
) -> list[str]:

    result: set[str] = set()

    patterns = [
        "CVCVCV",
        "CVCCVC",
        "CVCVCC",
        "VCVCVC",
        "CVVCVC",
        "CVCVC",
    ]

    for pattern in patterns:
        if len(pattern) != length:
            continue

        pools = []

        for char in pattern:
            if char == "C":
                pools.append(CONSONANTS)
            else:
                pools.append(VOWELS)

        for combination in product(*pools):
            candidate = "".join(combination)

            if candidate in result:
                continue

            result.add(candidate)

            if len(result) >= limit:
                return sorted(result)

    return sorted(result)


def generate_brand_candidates(
    length: int,
) -> list[str]:

    result: set[str] = set()

    for base in BRAND_BASES:
        base = normalize_username(base)

        if len(base) == length:
            result.add(base)

        if len(base) < length:
            for suffix in [
                "x",
                "a",
                "o",
                "y",
                "io",
                "ai",
                "lab",
                "hub",
                "pro",
            ]:
                candidate = base + suffix

                if len(candidate) == length:
                    result.add(candidate)

        if len(base) > length:
            result.add(base[:length])

    return sorted(result)


def generate_dictionary_candidates(
    length: int,
) -> list[str]:

    result: set[str] = set()

    for word in DICTIONARY_BASES:
        word = normalize_username(word)

        if len(word) == length:
            result.add(word)

    return sorted(result)


def generate_candidates(
    length: int,
    limit: int = 10000,
) -> list[str]:

    candidates: set[str] = set()

    candidates.update(
        generate_brand_candidates(length)
    )

    candidates.update(
        generate_dictionary_candidates(length)
    )

    candidates.update(
        generate_syllable_candidates(
            length=length,
            limit=limit,
        )
    )

    candidates.update(
        generate_vowel_pattern_candidates(
            length=length,
            limit=limit,
        )
    )

    clean = []

    for candidate in candidates:
        candidate = normalize_username(candidate)

        if not is_valid_username(candidate):
            continue

        if len(candidate) != length:
            continue

        clean.append(candidate)

        if len(clean) >= limit:
            break

    return sorted(set(clean))
