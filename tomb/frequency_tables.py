import lzma
from collections import Counter
from importlib import resources

from . import data
from .utils import freq, ngram_counter


english_char = Counter()
english_word = Counter()

english_bigram = Counter()
english_trigram = Counter()


for f in resources.contents(data):
    if f.endswith(".lzma"):
        with resources.open_binary(data, f) as src_b, lzma.open(src_b, "rt") as src_z:
            text = src_z.read().strip()
            freq(text, english_char)

            text = text.lower()
            freq((word.strip("!\"£$%^&*()-_=+{}[]:;@'~#<>,./?\\|") for word in text.split()), english_word)

            # bigram / trigram
            ngram_counter(text, 2, english_bigram)
            ngram_counter(text, 3, english_trigram)
