import re
from collections import deque, Counter, Iterable
from typing import Any, Callable, Optional, Union

# Assumptions:
#  - Textish instances have a .join() method.
#  - Textish instances can be created using an 0-arg constructor.
#  - Textish instances are iterable.
Textish = Union[str,bytes,bytearray]


def count_ngrams(
    data: Textish,
    n: int,
    tab: Optional[Counter[Textish]] = None,
    alphabet: Textish = "abcdefghijklmnopqrstuvwxyz"
) -> Counter[Textish]:
    """
    Count N-grams (bigrams, trigrams etc...) in text.

    Each character must be in the alphabet supplied.
    The type of data and alphabet must be compatible.
    Keys in the resultant counter will inherit the type of the alphabet.

    The default alphabet is a alphabetical string, in lowercase.
    """
    # Empty instance of alphabet's type is used to .join() on.
    # Allows str/bytes/bytearray to work as expected.
    e = type(alphabet)()
    if tab is None:
        tab = Counter()
    q = deque()
    for char in data:
        if char not in alphabet:
            q.clear()
            continue
        q.append(char)
        if len(q) < n:
            continue
        tab[e.join(q)] += 1
        q.popleft()
    return tab


def word_freq(
    s: str,
    tab: Optional[Counter[str]] = None,
    alphabet: str = "abcdefghijklmnopqrstuvwxyz-",
    scrub: Callable[[str], str] = lambda s: s.lstrip("-")
) -> Counter[str]:
    eal = re.escape(alphabet)
    raw = re.split(f"[^{eal}]+", s)
    scrubbed = filter(lambda s: s is not None and s != "", (scrub(word) for word in raw))
    return freq(scrubbed, tab)


def freq(s: Iterable[Any], tab: Optional[Counter[Any]] = None) -> Counter[Any]:
    if tab is None:
        tab = Counter()
    for c in s:
        tab[c] += 1
    return tab


def normalize(tab: Counter[Any]) -> dict[Any, float]:
    total = sum(tab.values())
    return {key: count / total for key, count in tab.most_common()}
