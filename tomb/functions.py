import math
from typing import Any, Union


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


# XXX: Remove in Python 3.10 - use int.bit_count instead.
_popcount_tbl = {b: bin(b).count("1") for b in range(0, 256)}

def hamming_distance(a: bytes, b: bytes) -> int:
    """
    Returns the hamming distance between two different binary strings of equal length.

    The hamming distance is the number of differing bits, i.e. the number of 1's in:

        a XOR b

    Raises a ValueError if arguments are of different length.
    """
    if len(a) != len(b):
        raise ValueError("The hamming distance between strings of unequal length is undefined.")

    d = 0

    for i, j in zip(a, b):
        c = i ^ j
        d += _popcount_tbl[c]
        #d += c.bit_count()
    return d
