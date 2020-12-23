import lzma
from importlib import resources

from .. import cache, data
from . import LanguageModel, LanguageModelData, analyse_language

def generate_language_model() -> LanguageModel:
    mdat = LanguageModelData.new()

    for f in resources.contents(data):
        if f.endswith(".lzma"):
            with resources.open_binary(data, f) as src_b, lzma.open(src_b, "rt") as src_z:
                text = src_z.read().strip()
                analyse_language(text, mdat)

    return mdat.normalize()


try:
    english = cache.unpickle("language-model-english")
except cache.CacheError:
    english = generate_language_model()
    cache.pickle("language-model-english", english)

