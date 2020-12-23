"""
Generic caching library for the tomb package.
"""

import io
import os
import pickle as mod_pickle

from typing import Any

TOMB_CACHE_DIR = os.path.join(
    os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
    "tomb"
)

try:
    os.makedirs(TOMB_CACHE_DIR, exist_ok=True)
    cache_available = True
except OSError:
    cache_available = False


class CacheError(Exception):
    pass


def cache_file_path(name: str) -> str:
    if "/" in name:
        raise ValueError("cache file name cannot contain slashes.")
    return os.path.join(TOMB_CACHE_DIR, name)


def invalidate(name: str):
    path = cache_file_path(name)
    if os.path.exists(path):
        os.unlink(path)


def exists(name: str) -> bool:
    return os.path.exists(cache_file_path(name))


def pickle(name: str, obj: Any):
    try:
        with open(cache_file_path(name), "wb") as f:
            return mod_pickle.dump(obj, f)
    except Exception as err:
        invalidate(name)
        raise CacheError("Failed to write/pickle cache object") from err


def unpickle(name: str) -> Any:
    try:
        with open(cache_file_path(name), "rb") as f:
            return mod_pickle.load(f)
    except Exception as err:
        invalidate(name)
        raise CacheError("Failed to read/unpickle cache object") from err
