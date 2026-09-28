"""
Matrices del código: B (dato del enunciado), G = [I | B] y H = [B | I].
"""

from . import linalg
from .bits import GF2, to_vec

B_ROWS = (
    0x98F, 0x4E7, 0x357, 0xBE2, 0xDD1, 0x7CC,
    0x53D, 0x2BE, 0x87B, 0xE74, 0xF1A, 0xEA9,
)

B = [to_vec(fila, 12) for fila in B_ROWS]
I12 = linalg.identity(12, GF2)
G = linalg.hstack(I12, B)
H = linalg.hstack(B, I12)
HT = linalg.transpose(H)


def b_is_symmetric():
    return linalg.equal(B, linalg.transpose(B))


def b_squared_is_identity():
    return linalg.equal(linalg.mat_mat(B, B), I12)


def g_h_are_orthogonal():
    return linalg.is_zero(linalg.mat_mat(G, HT))
