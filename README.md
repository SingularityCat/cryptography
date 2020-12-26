Cryptography stuff
------------------

Nothing much to see here.

The Python package called `tomb` is the beginnings of a cryptography toolkit.

It currently contains a disorganised mess of xor-ing functions, and a slightly
 more organised language analysis framework.

Points of interest:

 - `tomb.analysis` : Contains an "englishness" function.
 - `tomb.cache` : Generic caching code, currently caches models.
 - `tomb.counting` : Functions that produce/update/modify counters.
 - `tomb.functions` : Miscellaneous mathematical functions.
 - `tomb.language` : Language modeling code/package.
 - `tomb.language.data` : A selection of public domain non-fiction text.
 - `tomb.language.tables` : Builds char/word frequency tables from sample text.
