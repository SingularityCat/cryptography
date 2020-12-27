from collections.abc import Iterable, Iterator, Sequence
from typing import Any


def xorc(d: bytes, k: int) -> bytes:
    """
    XOR each byte with a single byte.
    """
    return bytes(b ^ k for b in d)


def infrep(seq: Iterable[Any]) -> Iterator[Any]:
    """Create an infinitely repeating sequence from a finite one."""
    while True:
        for i in seq:
            yield i


def xor(msg: bytes, key: bytes) -> bytes:
    """
    Compute the 'xor' of two byte strings, a message and a key.
    If the key is smaller than the message, it is repeated.
    """
    return bytes(x ^ y for x, y in zip(msg, infrep(key)))


def fission(fissile, *funcs):
    """
    Repeatedly apply an iterable of functions on the results of previous functions.
    e.g. let divmod2 = lambda n: divmod(n, 2)
    fission(9, divmod2)                   == [4, 1]
    fission(9, divmod2, divmod2)          == [[2, 0], [1, 0]]
    """
    if len(funcs) > 0:
        f = funcs[0]
        return [fission(seg, *funcs[1:]) for seg in f(fissile)]
    else:
        return fissile


def chop(s: Sequence[Any], k: int) -> list[Sequence[Any]]:
    """Chop some finite sequence up into groups of k length."""
    return [s[i:i+k] for i in range(0, len(s) - k, k)]


def nsplit(src: str, *delims: str):
    """
    Recursively split on a series of delimiters.
    e.g. nsplit(..., "\r\n", ":") would parse HTTP headers.
    """
    funcs = [lambda s, d=d: s.split(d) for d in delims]
    return fission(src, *funcs)


import pprint
pprint = pprint.PrettyPrinter(width=10, indent=4).pprint
