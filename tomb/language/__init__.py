from __future__ import annotations

from collections import Counter
from typing import Any, NamedTuple

from ..counting import freq, word_freq, count_ngrams, normalize


class LanguageModel(NamedTuple):
    char: dict[Any, float]
    word: dict[Any, float]
    bigram: dict[Any, float]
    trigram: dict[Any, float]


class LanguageModelData(NamedTuple):
    char: Counter[Any]
    word: Counter[Any]
    bigram: Counter[Any]
    trigram: Counter[Any]

    @staticmethod
    def new() -> LanguageModelData:
        return LanguageModelData(Counter(), Counter(), Counter(), Counter())

    def normalize(self) -> LanguageModel:
        return LanguageModel(
            normalize(self.char),
            normalize(self.word),
            normalize(self.bigram),
            normalize(self.trigram),
        )


def analyse_language(text: str, lmd: Optional[LanguageModelData] = None) -> LanguageModelData:
    if lmd is None:
        lmd = LanguageModelData.new()

    freq(text, lmd.char)

    text = text.lower()
    word_freq(text, lmd.word)

    # bigram / trigram
    count_ngrams(text, 2, lmd.bigram)
    count_ngrams(text, 3, lmd.trigram)

    return lmd
