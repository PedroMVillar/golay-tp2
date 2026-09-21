"""
Codificador de referencia y enumeración del código.

El codificador es matricial: ``v = m · G``, hecho con el producto
vector-matriz de :mod:`golay.linalg`. No se calcula la paridad por
ninguna vía alternativa, justamente porque el Ejercicio 5 pide construir
todo con esas operaciones.
"""

from collections import Counter
from functools import lru_cache

from fec_algebra import GF

from . import linalg
from .bits import GF2, CW_BITS, MSG_BITS, from_vec, to_vec
from .matrices import b_matrix, g_matrix, _as_lists


def parity(msg: int, field: GF = GF2) -> int:
    """Bits de paridad de un mensaje: ``p = m · B``, 12 bits."""
    vec = to_vec(msg, MSG_BITS, field)
    return from_vec(linalg.vec_mat(vec, _as_lists(b_matrix(field))))


def encode(msg: int, field: GF = GF2) -> int:
    """Codifica un mensaje de 12 bits en una palabra de 24: ``v = m · G``.

    Como ``G = [I | B]``, el resultado es el mensaje seguido de su
    paridad, pero se calcula con el producto matricial completo para que
    el modelo sea el que pide el enunciado y no un atajo equivalente.

    Raises:
        ValueError: si msg no entra en 12 bits.
    """
    vec = to_vec(msg, MSG_BITS, field)
    return from_vec(linalg.vec_mat(vec, _as_lists(g_matrix(field))))


@lru_cache(maxsize=None)
def all_codewords(field: GF = GF2) -> tuple:
    """Las 4096 palabras código, indexadas por mensaje.

    ``all_codewords()[m]`` es la palabra código del mensaje ``m``.
    Se cachea: construirla cuesta algo más de un segundo.
    """
    return tuple(encode(msg, field) for msg in range(1 << MSG_BITS))


@lru_cache(maxsize=None)
def weight_distribution(field: GF = GF2) -> Counter:
    """Distribución de pesos del código, por fuerza bruta (Ejercicio 5).

    Recorre las 4096 palabras y cuenta cuántas hay de cada peso. Para el
    Golay extendido tiene que dar ``{0:1, 8:759, 12:2576, 16:759, 24:1}``.
    """
    return Counter(
        linalg.weight(to_vec(cw, CW_BITS, field)) for cw in all_codewords(field)
    )


def minimum_distance(field: GF = GF2) -> int:
    """Distancia mínima del código: el peso mínimo no nulo.

    Vale porque el código es lineal: la distancia entre dos palabras es el
    peso de su suma, que también es una palabra código.
    """
    pesos = [w for w in weight_distribution(field) if w > 0]
    return min(pesos)
