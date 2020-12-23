import lzma
from importlib import resources

from .. import cache
from . import data
from . import LanguageModel, LanguageModelData, analyse_language

def generate_language_model(lang: str) -> LanguageModel:
    mdat = LanguageModelData.new()

    for f in resources.contents(data):
        if f.endswith(f".{lang}.lzma"):
            with resources.open_binary(data, f) as src_b, lzma.open(src_b, "rt") as src_z:
                text = src_z.read().strip()
                analyse_language(text, mdat)

    return mdat.normalize()


def load_language_model(lang: str) -> LanguageModel:
    try:
        lm = cache.unpickle(f"language-model-{lang}")
    except cache.CacheError:
        lm = generate_language_model(lang)
        cache.pickle(f"language-model-{lang}", lm)
    return lm


english = load_language_model("english")
