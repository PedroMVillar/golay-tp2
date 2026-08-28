"""
fec_algebra: librería chica para operar sobre campos de Galois GF(2^m)
y polinomios con coeficientes en esos campos.

Uso básico:

    from fec_algebra import GF, GFPoly

    field = GF(m=8, primitive_poly=0x1B)   # GF(2^8), primitivo del AES
    a = field(0x53)
    b = field(0xCA)

    c = a + b        # suma (XOR)
    d = a * b         # producto módulo el primitivo
    e = a.inverse()   # inverso multiplicativo (o ~a)
    f = a / b         # división
    g = a ** 5        # potencia

    p1 = GFPoly(field, [a, b, field(1)])
    p2 = GFPoly(field, [field(1), field(0)])
    s = p1 + p2
    prod = p1 * p2
    q, r = divmod(p1, p2)
    p3 = GFPoly.from_roots(field, [a, b])
"""

from .gf import GF
from .gf_element import GFElement
from .gf_poly import GFPoly
from .exceptions import (
    GFError,
    GFZeroDivisionError,
    GFFieldMismatchError,
    GFValueError,
)

__all__ = [
    "GF",
    "GFElement",
    "GFPoly",
    "GFError",
    "GFZeroDivisionError",
    "GFFieldMismatchError",
    "GFValueError",
]
