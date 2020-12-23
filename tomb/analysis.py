import math
import statistics
from typing import Any

from .language import analyse_language, tables


# The original approach taken here was to do a rank-scaled sum of differences between
#  the measured and reference distributions, and then average these scores.


def bhattacharyya_coefficient(p: dict[Any, float], q: dict[Any, float]) -> float:
    """
    Returns the Bhattacharyya coefficient for any two discrete probability distributions.

                  n  ____
        BC(p,q) = ∑ √pᵢqᵢ
                 i=1

    This is the sum, across all probabilities of the square root product of the same probability in p and q.

    Assuming probabilities in p and q correctly add up to 1.0 each, the output of this function is between
     0 and 1, with 0 meaning no overlap and 1 meaning total overlap.
    """
    return sum(math.sqrt(p.get(key, 0.0) * q.get(key, 0.0)) for key in p.keys() | q.keys())


def englishness(pt: str) -> float:
    """
    Calculates a "English score" -- the higher, the more likely some text is infact English.
    This score is the geometric mean of the Bhattacharyya coefficients of the following distributions:
     - characters
     - words
     - bigrams
     - trigrams

    An offset of 1 is added to each coefficient, this offset is subtracted from the resultant mean value.
    This avoids problems with the geometric mean when the coefficient is 0, but dampens the score penalty.

    Output is between 0 (probably not English) and 1 (a perfect sample of English, according to our dataset).
    """

    mod = analyse_language(pt).normalize()

    c = bhattacharyya_coefficient(mod.char,    tables.english.char)
    w = bhattacharyya_coefficient(mod.word,    tables.english.word)
    b = bhattacharyya_coefficient(mod.bigram,  tables.english.bigram)
    t = bhattacharyya_coefficient(mod.trigram, tables.english.trigram)

    return statistics.geometric_mean((c + 1.0, w + 1.0, b + 1.0, t + 1.0)) - 1.0
