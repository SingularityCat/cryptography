# Mathematical operations on GF(2⁸).

# What the hell is GF(2⁸)?
#
# You may want to refer to:
#  - https://www.doc.ic.ac.uk/~mrh/330tutor/ch04s02.html - quite pertinent, but also...
#  - https://en.wikipedia.org/wiki/Finite_field - and then probably...
#  - https://en.wikipedia.org/wiki/Field_(mathematics)
#
# But for my own convenience more than anyone, here's paraphrased/quoted important bits:
#
#
# This is the notation used to describe a finite field (also known as a Galois Field, after Évariste Galois).
#
# In algebra...
#  - A set is a well-defined collection of distinct elements.
#  - A field is a set with defined addition, subtraction, multiplication and division operations
#     that behave as they do on rational and real numbers (more or less).
#  - A finite field is a field with a finite number of elements.
#
# Specifically, a field is a set (let's call it F) along with two binary operations on F, addition and multiplication.
# These functions have a domain and codomain of F, that is, all possible inputs and outputs must be in F.
#
# The set and these functions must satisfy the following properties:
#  - Associativity, e.g.    a + (b + c) = (a + b) + c;      a × (b × c) = (a × b) × c.
#  - Commutativity, e.g.    a + b = b + a;                  a × b = b × a
#  - There must exist an identity for both addition (0) and multiplication (1), i.e:
#                           a + 0 = a                       a × 1 = a
#  - There must exist an additive inverse (-a) such that:
#                           a + -a = 0
#  - There must exist a multiplicative inverse (a⁻¹, where a ≠ 0) such that:
#                                                           a × a⁻¹ = 1
#  - Multiplication must distribute over addition:
#       a × (b + c) = (a × b) + (a × c)
#
#
# The existance of these inverses makes it possible to define subtraction and division as:
#   sub(a, b) = a + -b
#   div(a, b) = a × b⁻¹
#
#
# To understand fields better, consider these sets:
#   N - the set of all natural numbers (either all positive integers, or all non-negative integers).
#   Z - the set of all integers (positive, negative and zero).
#   Q - the set of all rational numbers (fractions).
#   R - the set of all real numbers (non-complex, but rational and irrationals, e.g. -1, 2, 0.5, 3.1415926...).
#
# N is not a field, as while addition and multiplication produce results inside the set, both inverses are missing.
#  (Alternatively, subtraction and division produce results outside the set.)
#
# Z is not a field - but it's closer. Addition works, and the additive inverse for all possible numbers is present,
#  but there is no multiplicative inverse. (Alternatively, division produces results outside the set.)
#
# Q is a field, as it's a superset of Z (logically, anything in Z could be written as an improper fraction like z/1),
#  and includes the multiplicative inverse of any fraction (simply swap the numerator and denominator).
#
# R is a field, almost by definition -- that's where we do real maths!
#
# Okay, none of those explanations are particularly rigorous in their definition,
#  but more importantly, none of those fields are finite fields, as they are all infinitely large.
#
# If we define addition and multiplication to be modular, i.e. operations are done modulo N, we can define
#  finite fields of integers.
#
# For example, if we do things modulo 5, i.e.  3 + 1 = 4, but  4 + 1 = 0 then the set:
#   {0, 1, 2, 3, 4}
#  is a finite field.
#
# The inverses are:
#       +   |       ×
#  --------------------
#   -0  0   | 0⁻¹  N/A      A multiplicative inverse of 0 is not required.
#   -1  4   | 1⁻¹   1
#   -2  3   | 2⁻¹   3
#   -3  2   | 3⁻¹   2
#   -4  1   | 4⁻¹   4
#
# This only works (with integer functions!) when the modulus is prime.
# A non-prime modulus means that some multiplicative inverses are missing, e.g. in modulo 8,
#  there are no numbers {0..7} that you can multiply by 4 modulo 8 to get 1.
#
# GF(2) simply means the set {0, 1} with addition and multiplication done modulo 2.
#
#
# So... what the hell is GF(2⁸)?
#
# GF(𝑝ⁿ) denotes a Galois Field of size 𝑝ⁿ, where arithmetic is done modulo 𝑝.
# Therefore, GF(2⁸) is a Galois field of size 256, where stuff happens modulo 2.
#
# Elements of such fields can be thought of and represented by polynomials.
#
# For example,
#   11 (dec) = 0x0A (hex) = 00001011 (bin)
# Can be represented as:
#   𝑥³ + 𝑥² + 1
# Or, in full form:
#   0𝑥⁷ + 0𝑥⁶ + 0𝑥⁵ + 0𝑥⁴ + 1𝑥³ + 1𝑥² + 0𝑥¹ + 1𝑥⁰
#
# This is important, as it kinda changes the definition of multiplication a bit...

# In GF(2⁸), addition is done modulo 2, which is the same as XOR.
# (XOR can also be thought of as addition without the carry.)

def gf2_8_add(a: int, b: int) -> int:
    return a ^ b


# Multiplication in GF(2⁸)/AES is done with the polynomial representation,
#  modulo the Rijndael reducing polynomial:
#   𝑥⁸ + 𝑥⁴ + 𝑥³ + 𝑥 + 1.
#   (or: 1000011011)
#
# Polynomial multiplication:
#  - Just expand it, e.g. (a + b) * (c + d) = (ac + ad + bc + bd)
#
# Polynomial long division:
#  - divide highest order term in the dividend by the highest order term
#     in the divisor, this one term of the dividend.
#  - multiply the divisor by the term derived, then subtract this from
#     the dividend...
#  - Repeat, using the result from the above step as the dividend
#
# Since we are operating in GF(2), addition and subtraction are the same,
#  and coefficients are all modulo 2, so any even coefficient = 0, and odd = 1.
#
# This means 3𝑥⁵ + 2𝑥 = 𝑥⁵ in GF(2)

def gf2_8_mul(x: int, y: int) -> int:
    # First, compute the product of polynomials x and y (m):
    # Note: the answer will always be within 16 bits.
    m = 0
    for bit in range(0, 8):
        n = (y >> bit) & 0x01
        m ^= n * (x << bit)

    # Then, compute m mod {100011011} (which is {11b})
    while True:
        m_ho_x = m.bit_length() - 1

        # Do the highest-order division -- these are exponents, so it's actually subtraction.
        if m_ho_x < 8:
            break
        q_x = m_ho_x - 8
        m ^= (0x11b << q_x)
        # Note: don't need the quotient, but logically, it'd be this:
        # q ^= (1 << q_x)

    return m
