#!/usr/bin/env python3

# Set 1, Challenge 1: hexstr to base64

from binascii import a2b_hex, b2a_base64

m_hex = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
m_raw = a2b_hex(m_hex)
m_b64 = b2a_base64(m_raw)

m_exp = "SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"

print(m_b4)

assert m_b64 == m_exp, "?"
