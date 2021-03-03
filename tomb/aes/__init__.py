"""
Reading resources:
 - https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
 - https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf

AES is a subset of the Rijndael family of ciphers standardized by NIST,
 the US "National Institute of Standards and Technology".

The Rijndael family of ciphers supported many different block/key sizes, specifically
 any block and any key length between 128 and 256 bits that is a multiple of 32 bits.

AES reduces this set to a fixed 128-bit block size, with either 128, 192 or 256 bit keys.
"""

import sys
from array import array
from typing import BinaryIO

from .io import *
from .modes import *


def load_key(key_bytes: bytes) -> array:
    if len(key_bytes) not in {16, 24, 32}:
        raise ValueError("Incorrect length for key.")

    key = array("I")
    key.frombytes(key_bytes)
    if sys.byteorder != "big":
        key.byteswap()
    return key


def encrypt(mode: AESMode, pt: bytes, key: bytes, *, pad: bool = True) -> bytes:
    key = load_key(key)

    biter = blockiter_mem(
        data := array("B", pt),
        PaddingMode.PAD if pad else PaddingMode.NONE
    )

    mode.encrypt(biter, key)

    return data.tobytes()


def decrypt(mode: AESMode, ct: bytes, key: bytes, *, pad: bool = True) -> bytes:
    key = load_key(key)

    biter = blockiter_mem(
        data := array("B", ct),
        PaddingMode.DEPAD if pad else PaddingMode.NONE
    )

    mode.decrypt(biter, key)

    return data.tobytes()


def encrypt_file(mode: AESMode, pt_src: BinaryIO, ct_dst: BinaryIO, key: bytes, *, pad: bool = True):
    key = load_key(key)

    biter = blockiter_io(
        pt_src,
        ct_dst,
        PaddingMode.PAD if pad else PaddingMode.NONE
    )

    mode.encrypt(biter, key)


def decrypt_file(mode: AESMode, ct_src: BinaryIO, pt_dst: BinaryIO, key: bytes, *, pad: bool = True):
    key = load_key(key)

    biter = blockiter_io(
        ct_src,
        pt_dst,
        PaddingMode.DEPAD if pad else PaddingMode.NONE
    )

    mode.decrypt(biter, key)
