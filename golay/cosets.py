"""
Tabla de síndromes armada a partir de H, y un decodificador por tabla.

Se usa como segundo decodificador para comparar contra el de cuatro
casos. Para cada síndrome se guardan todos los patrones de peso mínimo:
si hay uno solo se corrige, si hay varios el error no es corregible.
"""

from collections import Counter
from functools import lru_cache
from itertools import combinations

from .bits import split_cw
from .decoder import DecodeResult, syndrome


def error_patterns(peso):
    for pos in combinations(range(24), peso):
        e = 0
        for p in pos:
            e |= 1 << p
        yield e


@lru_cache(maxsize=None)
def coset_table():
    # recorriendo hasta peso 4 aparecen los 4096 síndromes
    tabla = {}
    for w in range(5):
        for e in error_patterns(w):
            s = syndrome(e)
            if s not in tabla:
                tabla[s] = (w, [e])
            elif tabla[s][0] == w:
                tabla[s][1].append(e)
    assert len(tabla) == 4096
    return tabla


def decode_by_table(rx):
    s = syndrome(rx)
    _, lideres = coset_table()[s]
    if len(lideres) > 1:
        return DecodeResult(0, 0, False, True, s, 5)
    err = lideres[0]
    msg, _ = split_cw(rx ^ err)
    return DecodeResult(msg, err, err != 0, False, s, 0)


def structure_summary():
    # (peso del líder, cantidad de líderes) -> cantidad de cosets
    return Counter((w, len(l)) for w, l in coset_table().values())
