#!/usr/bin/env python3
import operator
import functools

import pprint
import string
from binascii import hexlify, unhexlify

def simplify(s):
    """
    'Simplify' a string.
    Replaces all whitespace with spaces.
    Removes all non-ascii-alphanumeric chars (that aren't spaces).
    """
    trtbl = dict((ws, " ") for ws in string.whitespace)
    s = s.translate(trtbl)
    s = "".join(c for c in s if c in string.ascii_letters + string.digits + " ")
    return s.lower()


def freq(m, fmap=None):
    """Calculate the item occurance frequencies of some sequence."""
    if fmap is None:
        fmap = {}
    for c in m:
        if c in fmap:
            fmap[c] += 1
        else:
            fmap[c] = 1
    return fmap


def loadfreq(f, simple=True, word=False, fmap=None):
    """Load frequency data from a file."""
    if fmap is None:
        fmap = {}
    with open(f, "r") as src:
        for line in src:
            if simple:
                line = simplify(line)
            if word:
                freq(line.split(), fmap)
            else:
                freq(line, fmap)
    return fmap


def freqmap(a, b):
    """Create a translation table from frequency information."""
    s_a = sorted(a.items(), key=operator.itemgetter(1), reverse=True)
    s_b = sorted(b.items(), key=operator.itemgetter(1), reverse=True)
    mab = {}
    for a, b in zip(s_a, s_b):
        mab[ord(a[0])] = ord(b[0])
    return mab


def revmap(d: dict) -> dict:
    """Create a reversed mapping."""
    r = {}
    for k, v in d.items():
        r[v] = k
    return r


def rot(s: str, n: int, mod=256) -> str:
    """
    'rotate' every character in a string n times.
    (think rot13 or caesar)
    """
    def rotnum(k):
        return (mod + k + n) % mod
    return "".join(chr(rotnum(ord(c))) for c in s)


def infrep(seq):
    """Create an infinitely repeating sequence from a finite one."""
    while True:
        itr = iter(seq)
        for i in seq:
            yield i


def strxor(a: str, b: str) -> str:
    """
    Compute the 'xor' of two strings.
    If the strings are of different lengths, the smaller one is repeated.
    """
    m = max(a, b)
    k = infrep(min(a, b))
    return "".join(chr(ord(x) ^ ord(y)) for (x, y) in zip(m, k))


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


def chop(s, k):
    """Chop some finite sequence up into groups of k length."""
    return [s[i:i+k] for i in range(0, len(s) - k, k)]


def nsplit(src: str, *delims: str):
    """
    Recursively split on a series of delimiters.
    e.g. nsplit(..., "\r\n", ":") would parse HTTP headers.
    """
    funcs = [lambda s, d=d: s.split(d) for d in delims]
    return fission(src, *funcs)


def extract(src, *keys):
    for k in keys:
        src = src[k]
    return src

p = pprint.PrettyPrinter(width=10, indent=4).pprint
