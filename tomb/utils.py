from collections import deque, Counter, Iterable

from typing import Any, Optional


def ngram_counter(
    data: str,
    n: int,
    tab: Optional[Counter[str]] = None,
    alphabet: str = "abcdefghijklmnopqrstuvwxyz"
) -> Counter[str]:
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
        tab["".join(q)] += 1
        q.popleft()
    return tab


def freq(s: Iterable[Any], tab: Optional[Counter[Any]] = None) -> Counter[Any]:
    if tab is None:
        tab = Counter()
    for c in s:
        tab[c] += 1
    return tab
