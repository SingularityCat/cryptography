import math
import statistics
from collections.abc import Iterator
from typing import Any

from .functions import bhattacharyya_coefficient, hamming_distance
from .language import analyse_language, tables


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


def guess_vignere_key_length(ct: bytes, start: int = 1, end: int = -1, samples: int = -1) -> Iterator[int]:
    """
    Guess the key length for Vignére-like repeating key ciphers.
    Iterates over key length based on likelihood of correctness.

    This function assumes the plaintext is plain text (or something with similar non-uniformity).
    The technique used here works well for repeated-key XOR ciphers.

    If no bounds (key length range and number of Hamming distance samples) are provided, this function is O(n²).
    """
    mid = len(ct) // 2
    if end < 1 or end > mid:
        end = mid
    if samples < 1:
        samples = len(ct)

    guesses = {}

    # The lowest normalized Hamming distance between ct[len] and ct[len*2] is probably the key length.
    # This works if the plaintext is some semblance of a human-readable language.
    #
    # The reason for this is because edit distance between samples of such plaintext is usually limited,
    #  as they don't tend to be uniformly random in their representation, e.g. bytes of English ASCII text
    #  are likely to start with bits 01xxxxxx, with 010xxxxx being far more common.
    #
    # XOR ciphers (or, to a lesser extent, modular addition ala classic Vignére) will keep the Hamming
    #  distance between two pieces of ciphertext similar to that of the corresponding plaintexts.
    # In fact, for XOR, they are the same:
    #
    # >>> a, b = b"We will attack at dawn.", b"Can bring some alcohol."
    # >>> hamming_distance(a, b)
    #  55
    # >>> hamming_distance(xor(a, b"foo"), xor(b, b"foo"))
    #  55
    #
    # This is because XOR is it's own inverse (X ⊕ Y ⊕ X = Y), and an XOR operation is essentially how Hamming distance
    #  is computed, so given:
    #   A ⊕ K = C₁
    #   B ⊕ K = C₂
    # Then:
    #   C₁ ⊕ C₂ = A ⊕ B
    # K has been eliminated!
    #
    # However, the Hamming distance between two pieces of ciphertext XOR'd with a different key is generally
    #  higher, as the act of XOR'ing with a key will generally change which bits are more common.
    # The wrong keylength is essentially a different key, so K is NOT eliminated in this case,
    #  making the Hamming distance higher.

    for l in range(start, end + 1):
        num = 0
        dist = 0

        for i in range(0, min(samples, len(ct) // l) - 1):
            a = ct[(i + 0) * l : (i + 1) * l]
            b = ct[(i + 1) * l : (i + 2) * l]
            if len(a) != len(b):
                continue
            dist += hamming_distance(a, b) / l
            num += 1

        avg_norm_dist = dist / num

        guesses[l] = avg_norm_dist

    # Multiples of the correct key length will also have a low (possibly lower!) normalized Hamming distance.
    # This means if the key length is 29, 58 and 87 will also score well. It'd be nice to pick the right one.
    #
    # So, we filter by key lengths with a normalized Hamming distance lower than the mean + std deviation,
    #  then order by key length, before simply using Hamming distance alone.

    m = statistics.mean(guesses.values())
    d = statistics.stdev(guesses.values())

    more_likely = sorted(((l, sc) for l, sc in guesses.items() if (sc + d) - m < 0.0), key=lambda p: p[0])
    less_likely = sorted(((l, sc) for l, sc in guesses.items() if l not in {e for e, _ in more_likely}), key=lambda p: p[1])

    for l, _ in more_likely:
        yield l

    for l, _ in less_likely:
        yield l

    return more_likely + less_likely
