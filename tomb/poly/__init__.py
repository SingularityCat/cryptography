from __future__ import annotations

import re

from itertools import groupby
from typing import NamedTuple, Optional, Union


digit_to_unicode_superscript = {
    0: "⁰",
    1: "¹",
    2: "²",
    3: "³",
    4: "⁴",
    5: "⁵",
    6: "⁶",
    7: "⁷",
    8: "⁸",
    9: "⁹"
}

unicode_superscript_to_digit = {v: k for k, v in digit_to_unicode_superscript.items()}

unicode_superscript_digits = unicode_superscript_to_digit.keys()


def numeric_superscript(n: int) -> str:
    chars = []
    if n == 0:
        return digit_to_unicode_superscript[0]
    while n > 0:
        n, d = divmod(n, 10)
        chars.append(digit_to_unicode_superscript[d])
    return "".join(reversed(chars))


class Monomial(NamedTuple):
    coefficient: int
    exponent: int

    def fmt(self, varname: Optional[str] = None, simplify: bool = True) -> str:
        if varname is None:
            varname = "𝑥"

        if simplify and self.coefficient == 0:
            return "0"
        if simplify and self.exponent == 0:
            return str(self.coefficient)
        if simplify and self.coefficient == 1:
            coeff_str = ""
        else:
            coeff_str = str(self.coefficient)
        if simplify and self.exponent == 1:
            expo_str = ""
        else:
            expo_str = numeric_superscript(self.exponent)
        return coeff_str + varname + expo_str

    def __str__(self) -> str:
        return self.fmt()

    def __mul__(self, other: Monomial) -> Monomial:
        if not isinstance(other, Monomial): return NotImplemented
        return Monomial(self.coefficient * other.coefficient, self.exponent + other.exponent)

    def __floordiv__(self, other: Monomial) -> Monomial:
        if not isinstance(other, Monomial): return NotImplemented
        return divmod(self, other)[0]

    def __mod__(self, other: Monomial) -> Monomial:
        if not isinstance(other, Monomial): return NotImplemented
        return divmod(self, other)[1]

    def __divmod__(self, divisor: Monomial) -> Monomial:
        if not isinstance(divisor, Monomial): return NotImplemented

        if divisor.coefficient == 0:
            raise ZeroDivisionError("Cannot divide by zero!")

        d, r = divmod(self.coefficient, divisor.coefficient)
        e = self.exponent - divisor.exponent

        if e < 0:
            return Monomial(0, 0), self

        # is this right?
        return Monomial(d, e), Monomial(r, self.exponent)

    # Comparison operations (I implemented them all for some reason...)
    #
    # Mathematically speaking, any term with a coefficient of zero is equal to any other
    #  term with a coefficient of zero.
    # The __eq__ and __ne__ methods understand this, but I've left it out of the other comparisons.

    def __eq__(self, other: Monomial) -> bool:
        if 0 == self.coefficient == other.coefficient:
            return True
        return self.exponent == other.exponent and self.coefficient == other.coefficient

    def __ne__(self, other: Monomial) -> bool:
        if 0 == self.coefficient == other.coefficient:
            return False
        return self.exponent != other.exponent or self.coefficient != other.coefficient

    def __lt__(self, other: Monomial) -> bool:
        return self.exponent < other.exponent or \
            (self.exponent == other.exponent and self.coefficient < other.coefficient)

    def __le__(self, other: Monomial) -> bool:
        return self.exponent < other.exponent or \
            (self.exponent == other.exponent and self.coefficient <= other.coefficient)

    def __gt__(self, other: Monomial) -> bool:
        return self.exponent > other.exponent or \
            (self.exponent == other.exponent and self.coefficient > other.coefficient)

    def __ge__(self, other: Monomial) -> bool:
        return self.exponent > other.exponent or \
            (self.exponent == other.exponent and self.coefficient >= other.coefficient)


class Polynomial(NamedTuple):
    terms: tuple[Monomial, ...]

    def __len__(self) -> int:
        return len(self.terms)

    def fmt(self, varname: Optional[str] = None, simplify: bool = True) -> str:
        return " + ".join(
            term.fmt(varname, simplify) for term in self.terms if not simplify or term.coefficient != 0
        )

    def simplify(self, zero_terms: Union[int, bool] = False) -> Polynomial:
        terms = []
        for order, term_group in groupby(sorted(self.terms), lambda t: t.exponent):
            coeff = sum(term.coefficient for term in term_group)
            if zero_terms or coeff != 0:
                terms.append(Monomial(coeff, order))
        if isinstance(zero_terms, int):
            for order in range(0, zero_terms):
                if len(terms) > order and terms[order].exponent > order:
                    terms.insert(order, Monomial(0, order))
                elif len(terms) <= order:
                    terms.insert(order, Monomial(0, order))
        return Polynomial(tuple(reversed(terms)))

    def __str__(self) -> str:
        return " + ".join(term.fmt(simplify=True) for term in self.terms if term)

    def __neg__(self) -> Polynomial:
        return Polynomial(
            tuple(Monomial(-term.coefficient, term.exponent) for term in self.terms)
        )

    def __add__(self, other: Polynomial) -> Polynomial:
        return Polynomial(self.terms + other.terms).simplify()

    def __sub__(self, other: Polynomial) -> Polynomial:
        return self + -other

    def __mul__(self, other: Polynomial) -> Polynomial:
        return Polynomial(
            tuple(a * b for a in self.terms for b in other.terms)
        )

    def __divmod__(self, divisor: Polynomial) -> tuple[Polynomial, Polynomial]:
        assert len(self) != 0 and len(divisor) != 0

        dividend = self.simplify()
        divisor = divisor.simplify()

        quotient = []

        div_hio = divisor.terms[0]

        while True:
            quo_t, rem_t = divmod(dividend.terms[0], div_hio)
            if rem_t.coefficient != 0:
                break

            quotient.append(quo_t)
            dividend -= divisor * Polynomial((quo_t,))

        return Polynomial(quotient), dividend

    def __floordiv__(self, other: Polynomial) -> Polynomial:
        return divmod(self)[0]

    def __mod__(self, other: Polynomial) -> Polynomial:
        return divmod(self)[1]

    def __eq__(self, other: Polynomial) -> bool:
        for a, b in zip(self.simplify().terms, other.simplify.terms()):
            if a != b:
                return False
        return True


def parse_polynomial_forgiving(expr: str) -> Polynomial:
    """
    An extremely forgiving polynomial expression parser.
    Doesn't care about consistency, or a particular format.

    Essentially, looks for:
        [sign] [number] [anything] [number]

    The variable name can be _anything_ that isn't whitespace or +/-.
    The second number may be written using unicode superscript integers.

    Some strange examples:

        - "1&1 2&2" -> "𝑥 + 2𝑥²"
        - "4x³ + 2y^2 + 1z**1" -> "4𝑥³ + 2𝑥² + 𝑥"
    """
    terms = []
    src = iter(expr)

    while True:
        sign = 1
        coeff = 1
        expo = 0

        char = next(src, None)
        # parse sign, if any
        while char is not None and char in "+- \t":
            if char == "-":
                sign = -sign
            char = next(src, None)

        # parse coefficient, if specified
        if char is not None and char.isdigit():
            coeff = 0
            while char is not None and char.isdigit():
                coeff *= 10
                coeff += int(char)
                char = next(src, None)

        # "parse" variable and exponent operator
        while char is not None and not char.isdigit() and char not in "+- \t":
            expo = 1
            char = next(src, None)

        # parse exponent, if any
        if char is not None and (char.isdigit() or char in unicode_superscript_digits):
            expo = 0
            while char is not None and (char.isdigit() or char in unicode_superscript_digits):
                if char in unicode_superscript_digits:
                    digit = unicode_superscript_to_digit[char]
                else:
                    digit = int(char)
                expo *= 10
                expo += digit
                char = next(src, None)

        terms.append(Monomial(sign * coeff, expo))
        if char is None:
            break

    return Polynomial(tuple(terms))
