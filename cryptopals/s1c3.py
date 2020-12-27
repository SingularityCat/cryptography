#!/usr/bin/env python3

# Set 1, Challenge 3: XOR'd with single byte.

from binascii import unhexlify

from tomb import xorc
from tomb.analysis import englishness

ct = unhexlify(b"1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")

scores = {}
for k in range(0, 256):
    pt = xorc(ct, k)
    try:
        pt = pt.decode()
        sc = englishness(pt)
        scores[k] = sc
    except ValueError:
        pass

k = sorted(scores.items(), key=lambda p: p[1], reverse=True)[0][0]
print("key is likely: " + str(k))
print(xorc(ct, k).decode())
