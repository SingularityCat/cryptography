from array import array
from collections.abc import Iterator
from enum import IntEnum
from typing import BinaryIO


__all__ = ["blockiter_mem", "blockiter_io", "PaddingMode"]


def gen_padding(size: int) -> bytes:
    pad = 16 - (size & 0x0F)
    return bytes((pad,) * pad)


def chk_padding(size: int):
    if size > 16 or size < 1:
        raise ValueError("padding is rather strange.")


class PaddingMode(IntEnum):
    NONE = 0
    PAD = 1
    DEPAD = -1


def blockiter_mem(data: array, padding_mode: PaddingMode) -> Iterator[memoryview]:
    if padding_mode == PaddingMode.PAD:
        data.frombytes(gen_padding(len(data)))
    elif (len(data) & 0x0F) > 0:
        raise ValueError("Data not a multiple of block length (no padding?)")

    buf = memoryview(data)
    for idx in range(0, len(data), 16):
        seg = buf[idx:idx+16]
        yield seg
        seg.release()
    buf.release()

    if padding_mode == PaddingMode.DEPAD:
        pad = data[-1]
        chk_padding(pad)
        del data[-pad:]


def blockiter_io(src: BinaryIO, dst: BinaryIO, padding_mode: PaddingMode) -> Iterator[memoryview]:
    nxt_blk = src.read(16)
    more = True

    while more:
        cur_blk = nxt_blk
        nxt_blk = src.read(16)

        if len(cur_blk) < 16:
            more = False
            if padding_mode == PaddingMode.PAD:
                cur_blk += gen_padding(len(cur_blk))
            elif len(cur_blk) != 0:
                raise ValueError("Data not a multiple of block length (no padding?)")

        data = array("B", cur_blk)
        buf = memoryview(data)
        yield buf
        buf.release()

        if padding_mode == PaddingMode.DEPAD and len(nxt_blk) == 0:
            more = False
            pad = data[-1]
            chk_padding(pad)
            del data[-pad:]

        dst.write(data.tobytes())
