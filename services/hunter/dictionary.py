from dataclasses import dataclass


@dataclass(frozen=True)
class DictionaryWord:
    word: str
    category: str
    commercial_score: float


WORDS = [
    DictionaryWord("aura", "brand", 8.5),
    DictionaryWord("nova", "brand", 9.0),
    DictionaryWord("luna", "brand", 8.5),
    DictionaryWord("vela", "brand", 8.0),
    DictionaryWord("vera", "brand", 8.0),
    DictionaryWord("nexa", "brand", 8.5),
    DictionaryWord("zora", "brand", 8.0),
    DictionaryWord("riva", "brand", 7.5),
    DictionaryWord("mira", "brand", 7.5),
    DictionaryWord("sora", "brand", 7.5),
    DictionaryWord("nora", "brand", 7.0),
    DictionaryWord("solar", "nature", 8.5),
    DictionaryWord("orbit", "space", 8.5),
    DictionaryWord("prime", "business", 9.0),
    DictionaryWord("royal", "luxury", 9.0),
    DictionaryWord("elite", "luxury", 9.0),
    DictionaryWord("valor", "brand", 8.5),
    DictionaryWord("vision", "business", 8.0),
    DictionaryWord("future", "business", 8.0),
    DictionaryWord("legend", "brand", 8.5),
    DictionaryWord("vector", "technology", 7.5),
    DictionaryWord("vertex", "technology", 8.0),
    DictionaryWord("pixel", "technology", 8.0),
    DictionaryWord("orbit", "space", 8.5),
    DictionaryWord("crypto", "finance", 8.5),
    DictionaryWord("token", "finance", 8.0),
    DictionaryWord("market", "business", 8.0),
    DictionaryWord("studio", "business", 7.0),
    DictionaryWord("digital", "technology", 7.5),
    DictionaryWord("future", "technology", 8.0),
    DictionaryWord("dream", "general", 7.5),
    DictionaryWord("cloud", "technology", 7.5),
    DictionaryWord("swift", "brand", 8.0),
    DictionaryWord("spark", "brand", 8.0),
    DictionaryWord("pulse", "brand", 8.0),
    DictionaryWord("flash", "brand", 8.0),
    DictionaryWord("storm", "brand", 8.0),
    DictionaryWord("prime", "business", 9.0),
    DictionaryWord("crown", "luxury", 8.5),
    DictionaryWord("gold", "luxury", 9.0),
    DictionaryWord("silver", "luxury", 7.5),
    DictionaryWord("black", "brand", 8.0),
    DictionaryWord("white", "brand", 7.0),
    DictionaryWord("green", "general", 6.5),
    DictionaryWord("ocean", "nature", 7.5),
    DictionaryWord("river", "nature", 7.0),
    DictionaryWord("stone", "general", 7.0),
    DictionaryWord("light", "general", 7.5),
    DictionaryWord("bright", "general", 7.5),
    DictionaryWord("magic", "general", 8.0),
    DictionaryWord("dream", "general", 7.5),
]


def get_words(
    length: int | None = None,
) -> list[DictionaryWord]:

    if length is None:
        return WORDS.copy()

    return [
        word
        for word in WORDS
        if len(word.word) == length
    ]


def find_word(
    word: str,
) -> DictionaryWord | None:

    word = word.lower().strip()

    for item in WORDS:
        if item.word == word:
            return item

    return None


def dictionary_candidates(
    length: int,
) -> list[str]:

    return [
        item.word
        for item in get_words(length)
    ]
