"""
Ejercicio 4. Primero me fijo que la librería del TP1 con m = 1 se comporte
como GF(2): sumar es XOR, multiplicar es AND y el único que tiene inverso
es el 1. Después pruebo las operaciones de matrices nuevas con ejemplos
chicos que se pueden hacer a mano.
"""

import pytest

from fec_algebra import GFZeroDivisionError
from golay import GF2, from_vec, to_vec
from golay import linalg


def test_campo_de_dos_elementos():
    assert GF2.order == 2


def test_suma_es_xor():
    for a in (0, 1):
        for b in (0, 1):
            assert int(GF2(a) + GF2(b)) == a ^ b


def test_producto_es_and():
    for a in (0, 1):
        for b in (0, 1):
            assert int(GF2(a) * GF2(b)) == a & b


def test_inverso():
    assert int(~GF2(1)) == 1
    with pytest.raises(GFZeroDivisionError):
        ~GF2(0)


def test_conversion_de_bits():
    # el elemento 0 del vector es el bit más significativo
    assert [int(x) for x in to_vec(0b1000, 4)] == [1, 0, 0, 0]
    assert from_vec(to_vec(0xA5C, 12)) == 0xA5C


def test_vec_mat():
    # [1,1] · [[1,1],[0,1]] = [1, 1+1] = [1, 0]
    m = [[GF2(1), GF2(1)], [GF2(0), GF2(1)]]
    v = [GF2(1), GF2(1)]
    assert [int(x) for x in linalg.vec_mat(v, m)] == [1, 0]


def test_mat_mat():
    # [[1,1],[0,1]] al cuadrado da la identidad en GF(2)
    m = [[GF2(1), GF2(1)], [GF2(0), GF2(1)]]
    assert linalg.equal(linalg.mat_mat(m, m), linalg.identity(2, GF2))


def test_peso():
    assert linalg.weight(to_vec(0x000, 12)) == 0
    assert linalg.weight(to_vec(0xFFF, 12)) == 12
    assert linalg.weight(to_vec(0x98F, 12)) == 7   # la fila b_0
