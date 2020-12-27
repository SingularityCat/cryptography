#!/usr/bin/env python3

# Set 1, Challenge 5: Implement repeating-key XOR.

from binascii import hexlify

from tomb import xor

pt = """\
Burning 'em, if you ain't quick and nimble
I go crazy when I hear a cymbal""".encode()

ct = xor(pt, b"ICE")

exp_ct_hex = b"0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a26226324272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b20283165286326302e27282f"

print(hexlify(ct).decode())

assert hexlify(ct) == exp_ct_hex, "?"
