from services.hunter.beauty import (
    beauty_score,
    length_score,
    readability_score,
)
from services.hunter.dictionary import (
    find_word,
)


def rank_username(
    username: str,
) -> float:

    beauty = beauty_score(username)
    readability = readability_score(username)
    length = length_score(username)

    dictionary = find_word(username)

    dictionary_bonus = 0.0

    if dictionary:
        dictionary_bonus = (
            dictionary.commercial_score * 0.5
        )

    return round(
        beauty * 0.45
        + readability * 0.25
        + length * 0.10
        + dictionary_bonus * 0.20,
        2,
    )


def rank_usernames(
    usernames: list[str],
) -> list[str]:

    return sorted(
        set(usernames),
        key=rank_username,
        reverse=True,
    )
