import lzma
from collections import Counter
from importlib import resources

from . import data
from .utils import freq, word_freq, count_ngrams, normalize


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
            word_freq(text, english_word)

            # bigram / trigram
            count_ngrams(text, 2, english_bigram)
            count_ngrams(text, 3, english_trigram)


english_char_normalized = normalize(english_char)
english_word_normalized = normalize(english_word)
english_bigram_normalized = normalize(english_bigram)
english_trigram_normalized = normalize(english_trigram)

