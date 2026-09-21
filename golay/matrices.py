"""
Las matrices del código: B, G = [I | B] y H = [B | I].

``B_ROWS`` es el único dato duro del modelo: son las doce constantes que
da el enunciado, idénticas para todos los grupos. Todo lo demás se
construye con las operaciones de :mod:`golay.linalg`, como pide el
Ejercicio 5.

Este módulo también expone las tres verificaciones del Ejercicio 1, para
que los tests y el script de caracterización usen exactamente el mismo
código y no dos implementaciones que podrían discrepar.
"""

from functools import lru_cache

from fec_algebra import GF

from . import linalg
from .bits import GF2, MSG_BITS, PAR_BITS, to_vec

#: Las doce filas de B, tal cual las da el enunciado (b_0 .. b_11).
B_ROWS = (
    0x98F, 0x4E7, 0x357, 0xBE2, 0xDD1, 0x7CC,
    0x53D, 0x2BE, 0x87B, 0xE74, 0xF1A, 0xEA9,
)


@lru_cache(maxsize=None)
def b_matrix(field: GF = GF2) -> tuple:
    """La matriz B, de 12×12.

    La fila ``i`` es ``b_i`` y el bit ``[11-j]`` de ``b_i`` es ``B[i][j]``,
    que es la convención del enunciado (ver :mod:`golay.bits`).
    """
    return tuple(tuple(to_vec(row, PAR_BITS, field)) for row in B_ROWS)


@lru_cache(maxsize=None)
def g_matrix(field: GF = GF2) -> tuple:
    """La matriz generadora ``G = [ I_12 | B ]``, de 12×24."""
    izq = linalg.identity(MSG_BITS, field)
    return tuple(tuple(fila) for fila in linalg.hstack(izq, _as_lists(b_matrix(field))))


@lru_cache(maxsize=None)
def h_matrix(field: GF = GF2) -> tuple:
    """La matriz de chequeo de paridad ``H = [ B | I_12 ]``, de 12×24."""
    der = linalg.identity(PAR_BITS, field)
    return tuple(tuple(fila) for fila in linalg.hstack(_as_lists(b_matrix(field)), der))


@lru_cache(maxsize=None)
def h_transpose(field: GF = GF2) -> tuple:
    """``H^T``, de 24×12. Es con lo que se calcula el síndrome ``s = r · H^T``."""
    return tuple(tuple(fila) for fila in linalg.transpose(_as_lists(h_matrix(field))))


def _as_lists(mat: tuple) -> list:
    """Las matrices se cachean como tuplas (hashables); linalg trabaja con listas."""
    return [list(fila) for fila in mat]


# ------------------------------------------------ verificaciones del Ej. 1
def b_is_symmetric(field: GF = GF2) -> bool:
    """¿Es ``B = B^T``?"""
    b = _as_lists(b_matrix(field))
    return linalg.equal(b, linalg.transpose(b))


def b_squared_is_identity(field: GF = GF2) -> bool:
    """¿Es ``B^2 = I_12``?"""
    b = _as_lists(b_matrix(field))
    return linalg.equal(linalg.mat_mat(b, b), linalg.identity(PAR_BITS, field))


def g_h_are_orthogonal(field: GF = GF2) -> bool:
    """¿Es ``G · H^T = 0``?

    Es la condición que define a H como matriz de chequeo de G: toda
    palabra código tiene síndrome nulo.
    """
    g = _as_lists(g_matrix(field))
    ht = _as_lists(h_transpose(field))
    return linalg.is_zero(linalg.mat_mat(g, ht))


def check_all(field: GF = GF2) -> dict:
    """Corre las tres verificaciones y devuelve un dict con los resultados."""
    return {
        "B = B^T": b_is_symmetric(field),
        "B^2 = I": b_squared_is_identity(field),
        "G H^T = 0": g_h_are_orthogonal(field),
    }
