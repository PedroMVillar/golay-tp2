"""
Pasaje entre enteros y vectores de GF(2).

Convención del enunciado: cw[23:12] es el mensaje, cw[11:0] la paridad,
y el elemento 0 del vector es el bit más significativo del entero.
"""

from fec_algebra import GF

# GF(2^1) con P(x) = x + 1, o sea GF(2)
GF2 = GF(m=1, primitive_poly=0b1)

MSG_BITS = 12
PAR_BITS = 12


def to_vec(value, width):
    return [GF2((value >> (width - 1 - i)) & 1) for i in range(width)]


def from_vec(vec):
    out = 0
    for coef in vec:
        out = (out << 1) | int(coef)
    return out


def unit_int(i, width=MSG_BITS):
    return 1 << (width - 1 - i)


def split_cw(cw):
    return cw >> PAR_BITS, cw & 0xFFF


def join_cw(msg, par):
    return (msg << PAR_BITS) | par
