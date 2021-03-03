import sys
from array import array
from collections.abc import Iterator
from typing import NamedTuple, Callable

from .core import key_expansion, cipher, inv_cipher, xor_state


class AESMode(NamedTuple):
    name: str
    longname: str
    encrypt: Callable[[Iterator[memoryview], array], None]
    decrypt: Callable[[Iterator[memoryview], array], None]


modes = {}


def defmode(*args) -> AESMode:
    mode = AESMode(*args)
    modes[mode.name] = mode
    return mode


def ecb_encrypt(pt: Iterator[memoryview], key: array):
    w = key_expansion(key)
    for state in pt:
        cipher(state, w)


def ecb_decrypt(ct: Iterator[memoryview], key: array):
    w = key_expansion(key)
    for state in ct:
        inv_cipher(state, w)


ECB = defmode("ECB", "Electronic Code Book", ecb_encrypt, ecb_decrypt)


def cbc_encrypt(pt: Iterator[memoryview], key: array):
    w = key_expansion(key)
    #p = iv
    p = array("B", b"\x00"*16)
    for state in pt:
        xor_state(state, p)
        cipher(state, w)
        p = array("B", state)


def cbc_decrypt(pt: Iterator[memoryview], key: array):
    w = key_expansion(key)
    #p = iv
    p = array("B", b"\x00"*16)
    for state in pt:
        n = array("B", state)
        inv_cipher(state, w)
        xor_state(state, p)
        p = n


CBC = defmode("CBC", "Cipher Block Chaining", cbc_encrypt, cbc_decrypt)


