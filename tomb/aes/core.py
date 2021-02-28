# Reading resources:
#  - https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
#  - https://en.wikipedia.org/wiki/AES_key_schedule
#  - https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf

"""
AES core routines.

This module follows strict conventions - the appropriate type, length and mutability
 of an array argument can be determined from it's name.

**state array**
The state array is an array of 16 unsigned 8-bit integers.
This array is always modified by the subroutine it's passed to.

This represents the "state" concept in AES, and should hold the input/output plaintext/ciphertext.
This array is actually a column-major 4x4 array.

    state[i,j] = state[i + j*4]


**key array**
The key array is an array of 4, 6 or 8 unsigned 32-bit integers.
This array is read-only.

This represents a 128, 192 or 256 bit AES key.


**keysched array**
The keysched array is an array of 44, 52 or 60 unsigned 32-bit integers.
This array is read-only.

This represents the key schedule of an AES key.

---

These functions generally trust the above is true.
"""

from array import array

from .constants import *


def fmt_state(state: array) -> str:
    return "\n".join(" ".join(f"{state[j + 4*i]:02x}" for i in range(0, 4)) for j in range(0, 4))


ZEROES = b"\x00\x00\x00\x00" * 60   # largest size of key schedule


def key_expansion(key: array) -> array:
    keysched = key[:]

    # Length of the key, in 32-bit words.
    # should be 4, 6 or 8.
    nk = len(keysched)

    # Number of rounds.
    # nk | nr
    # -------
    #  4 | 10
    #  6 | 12
    #  8 | 14
    nr = nk + 6

    # Pad out key schedule array to it's appropriate size.
    # Total length should be 44, 52 or 60 words.
    keysched.frombytes(ZEROES[:((nr + 1) * 4 - nk) * 4])

    for i in range(nk, len(keysched)):
        t = keysched[i - 1]
        if i % nk == 0:
            t = kex_sub_word(kex_rot_word(t)) ^ R_CON[i//nk - 1]
        elif nk > 6 and i % nk == 4:
            t = kex_sub_word(t)
        keysched[i] = keysched[i-nk] ^ t

    return keysched


# Functions for key_expansion (kex)

def kex_sub_word(w: int) -> int:
    r = 0
    for b in range(0, 32, 8):
        r |= S_BOX[w >> b & 0xFF] << b
    return r


def kex_rot_word(w: int) -> int:
    r = w << 8
    r |= w >> 24
    return r & 0xFFFFFFFF


# That's it for key_expansion.


def add_round_key(state: array, keysched: array, r: int):
    for c in range(0, 4):
        ksw = keysched[r*4 + c]
        state[0 + c*4] ^= (ksw >> 24) & 0xFF
        state[1 + c*4] ^= (ksw >> 16) & 0xFF
        state[2 + c*4] ^= (ksw >>  8) & 0xFF
        state[3 + c*4] ^= (ksw >>  0) & 0xFF


def sub_bytes(state: array):
    # Substitute values in the AES S-box.
    for i in range(0, 16):
        state[i] = S_BOX[state[i]]


# State is column major, so:
#
# [ 0,  4,  8, 12]
# [ 1,  5,  9, 13]
# [ 2,  6, 10, 14]
# [ 3,  7, 11, 15]


def shift_rows(state: array):
    t1 = state[1]
    state[1] = state[5]
    state[5] = state[9]
    state[9] = state[13]
    state[13] = t1

    t2 = state[2]
    t6 = state[6]
    state[2] = state[10]
    state[6] = state[14]
    state[10] = t2
    state[14] = t6

    t3 = state[3]
    state[3] = state[15]
    state[15] = state[11]
    state[11] = state[7]
    state[7] = t3


def mix_columns(state: array):
    # Treating each column of state as a 4-term polynomial,
    #  multiply by '3𝑥³ + 𝑥² + 𝑥 + 2' modulo '𝑥⁴ + 1'
    # Apparently, this is equivalent to this matrix multiplication in GF(2⁸):
    #
    # [Sa']   [2 3 1 1] [Sa]
    # [Sb']   [1 2 3 1] [Sb]
    # [Sc'] = [1 1 2 3] [Sc]
    # [Sd']   [3 1 1 2] [Sd]

    for c in range(0, 16, 4):
        sc0 = GMUL2_LUT[state[0 + c]] ^ GMUL3_LUT[state[1 + c]] ^           state[2 + c]  ^           state[3 + c]
        sc1 =           state[0 + c]  ^ GMUL2_LUT[state[1 + c]] ^ GMUL3_LUT[state[2 + c]] ^           state[3 + c]
        sc2 =           state[0 + c]  ^           state[1 + c]  ^ GMUL2_LUT[state[2 + c]] ^ GMUL3_LUT[state[3 + c]]
        sc3 = GMUL3_LUT[state[0 + c]] ^           state[1 + c]  ^           state[2 + c]  ^ GMUL2_LUT[state[3 + c]]

        state[0 + c] = sc0
        state[1 + c] = sc1
        state[2 + c] = sc2
        state[3 + c] = sc3


def inv_sub_bytes(state: array):
    for i in range(0, 16):
        state[i] = INV_S_BOX[state[i]]


def inv_shift_rows(state: array):
    t1 = state[1]
    state[1] = state[13]
    state[13] = state[9]
    state[9] = state[5]
    state[5] = t1

    t2 = state[2]
    t6 = state[6]
    state[2] = state[10]
    state[6] = state[14]
    state[10] = t2
    state[14] = t6

    t3 = state[3]
    state[3] = state[7]
    state[7] = state[11]
    state[11] = state[15]
    state[15] = t3


def inv_mix_columns(state: array):
    # Treating each column of state as a 4-term polynomial,
    #  multiply by '11𝑥³ + 13𝑥² + 9𝑥 + 14' modulo '𝑥⁴ + 1'
    # Apparently, this is equivalent to this matrix multiplication:
    #
    # [Sa']   [14 11 13  9] [Sa]
    # [Sb']   [ 9 14 11 13] [Sb]
    # [Sc'] = [13  9 14 11] [Sc]
    # [Sd']   [11 13  9 14] [Sd]

    for c in range(0, 16, 4):
        sc0 = GMUL14_LUT[state[0 + c]] ^ GMUL11_LUT[state[1 + c]] ^ GMUL13_LUT[state[2 + c]] ^ GMUL09_LUT[state[3 + c]]
        sc1 = GMUL09_LUT[state[0 + c]] ^ GMUL14_LUT[state[1 + c]] ^ GMUL11_LUT[state[2 + c]] ^ GMUL13_LUT[state[3 + c]]
        sc2 = GMUL13_LUT[state[0 + c]] ^ GMUL09_LUT[state[1 + c]] ^ GMUL14_LUT[state[2 + c]] ^ GMUL11_LUT[state[3 + c]]
        sc3 = GMUL11_LUT[state[0 + c]] ^ GMUL13_LUT[state[1 + c]] ^ GMUL09_LUT[state[2 + c]] ^ GMUL14_LUT[state[3 + c]]

        state[0 + c] = sc0
        state[1 + c] = sc1
        state[2 + c] = sc2
        state[3 + c] = sc3


# The AES cipher/inverse cipher

def cipher(state: array, keysched: array):
    rounds = (len(keysched) >> 2) - 1
    add_round_key(state, keysched, 0)

    for r in range(1, rounds):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, keysched, r)

    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, keysched, rounds)


def inv_cipher(state: array, keysched: array):
    rounds = (len(keysched) >> 2) - 1
    add_round_key(state, keysched, rounds)

    # more readable: reversed(range(1, rounds))
    for r in range(rounds - 1, 0, -1):
        inv_shift_rows(state)
        inv_sub_bytes(state)
        add_round_key(state, keysched, r)
        inv_mix_columns(state)

    inv_shift_rows(state)
    inv_sub_bytes(state)
    add_round_key(state, keysched, 0)
