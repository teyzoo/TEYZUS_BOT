from itertools import product


LETTERS = "abcdefghijklmnopqrstuvwxyz"


def validate_mask(mask: str) -> bool:
    mask = mask.lower().strip()

    if not 5 <= len(mask) <= 32:
        return False

    return all(
        char == "?"
        or char in LETTERS
        for char in mask
    )


def generate_from_mask(
    mask: str,
    limit: int = 5000,
) -> list[str]:

    mask = mask.lower().strip()

    if not validate_mask(mask):
        return []

    unknown_count = mask.count("?")

    if unknown_count == 0:
        return [mask]

    if unknown_count > 5:
        return []

    positions = [
        index
        for index, char in enumerate(mask)
        if char == "?"
    ]

    result = []

    for letters in product(
        LETTERS,
        repeat=unknown_count,
    ):

        chars = list(mask)

        for position, letter in zip(
            positions,
            letters,
        ):
            chars[position] = letter

        result.append(
            "".join(chars)
        )

        if len(result) >= limit:
            break

    return result
