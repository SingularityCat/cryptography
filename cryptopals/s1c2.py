#!/usr/bin/env python3

# Set 1, Challenge 2: XOR two strings

from binascii import hexlify, unhexlify

from tomb import xor

def hexor(a: str, b: str) -> str:
    return hexlify(xor(unhexlify(a.encode()), unhexlify(b.encode()))).decode()

gen_ct = hexor("1c0111001f010100061a024b53535009181c", "686974207468652062756c6c277320657965")
exp_ct = "746865206b696420646f6e277420706c6179"

print(gen_ct)

assert gen_ct == exp_ct, "?"
