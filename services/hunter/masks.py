import re


def validate_mask(mask: str) -> bool:
    mask = mask.lower().strip()

    if not 5 <= len(mask) <= 32:
        return False

    return bool(
        re.fullmatch(
            r"[a-z0-9?]+",
            mask,
        )
    )


def matches_mask(
    username: str,
    mask: str,
) -> bool:

    username = username.lower()
    mask = mask.lower()

    if len(username) != len(mask):
        return False

    for char, pattern in zip(
        username,
        mask,
    ):
        if pattern == "?":
            continue

        if char != pattern:
            return False

    return True


def mask_to_regex(mask: str) -> str:
    parts = []

    for char in mask:
        if char == "?":
            parts.append("[a-z]")
        else:
            parts.append(re.escape(char))

    return "^" + "".join(parts) + "$"
