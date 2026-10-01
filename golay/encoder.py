"""
Codificador (v = m · G) y enumeración de las 4096 palabras código.
"""

from collections import Counter
from functools import lru_cache

from . import linalg
from .bits import from_vec, to_vec
from .matrices import G


def encode(msg):
    return from_vec(linalg.vec_mat(to_vec(msg, 12), G))


@lru_cache(maxsize=None)
def all_codewords():
    return tuple(encode(m) for m in range(4096))


@lru_cache(maxsize=None)
def weight_distribution():
    return Counter(linalg.weight(to_vec(cw, 24)) for cw in all_codewords())


def minimum_distance():
    return min(w for w in weight_distribution() if w > 0)
