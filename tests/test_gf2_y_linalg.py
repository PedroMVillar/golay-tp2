"""
Ejercicio 4. Primero me fijo que la librería del TP1 con m = 1 se comporte
como GF(2): sumar es XOR, multiplicar es AND y el único que tiene inverso
es el 1. Después pruebo las operaciones de matrices nuevas con ejemplos
chicos que se pueden hacer a mano.
"""

import pytest

from fec_algebra import GF, GFZeroDivisionError
from golay import GF2, from_vec, to_vec
from golay import linalg


class TestGF2:

    def test_orden(self, gf2):
        assert gf2.order == 2
        assert gf2.m == 1

    @pytest.mark.parametrize("a,b,esperado", [
        (0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0),
    ])
    def test_suma_es_xor(self, gf2, a, b, esperado):
        assert int(gf2(a) + gf2(b)) == esperado

    @pytest.mark.parametrize("a,b,esperado", [
        (0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1),
    ])
    def test_producto_es_and(self, gf2, a, b, esperado):
        assert int(gf2(a) * gf2(b)) == esperado

    def test_inverso_del_uno(self, gf2):
        assert int(~gf2(1)) == 1

    def test_el_cero_no_tiene_inverso(self, gf2):
        with pytest.raises(GFZeroDivisionError):
            ~gf2(0)

    def test_no_hizo_falta_tocar_la_libreria(self):
        campo = GF(m=1, primitive_poly=0b1)
        assert campo == GF2
        assert [int(campo(v)) for v in range(campo.order)] == [0, 1]
        assert int(campo.power(1, 0)) == 1
        assert int(campo.divide(1, 1)) == 1


class TestBits:

    def test_el_elemento_cero_es_el_msb(self):
        v = to_vec(0b100000000000, 12)
        assert int(v[0]) == 1
        assert all(int(x) == 0 for x in v[1:])

    def test_ida_y_vuelta(self):
        for valor in (0x000, 0x001, 0x98F, 0xA5C, 0xFFF):
            assert from_vec(to_vec(valor, 12)) == valor


class TestLinalg:

    def test_identidad_es_neutro(self, gf2):
        ident = linalg.identity(4, gf2)
        m = [to_vec(v, 4) for v in (0b1011, 0b0110, 0b1111, 0b0001)]
        assert linalg.equal(linalg.mat_mat(m, ident), m)
        assert linalg.equal(linalg.mat_mat(ident, m), m)

    def test_vec_mat_suma_las_filas_marcadas(self, gf2):
        m = [to_vec(v, 4) for v in (0b1000, 0b0100, 0b0010, 0b0001)]
        v = to_vec(0b1010, 4)
        assert from_vec(linalg.vec_mat(v, m)) == 0b1010

    def test_vec_mat_a_mano(self, gf2):
        # [1,1] · [[1,1],[0,1]] = [1, 0]
        m = [[gf2(1), gf2(1)], [gf2(0), gf2(1)]]
        v = [gf2(1), gf2(1)]
        assert [int(x) for x in linalg.vec_mat(v, m)] == [1, 0]

    def test_mat_mat_asociativo(self, gf2):
        a = [to_vec(v, 3) for v in (0b101, 0b011, 0b110)]
        b = [to_vec(v, 3) for v in (0b001, 0b111, 0b010)]
        v = to_vec(0b101, 3)
        izq = linalg.vec_mat(linalg.vec_mat(v, a), b)
        der = linalg.vec_mat(v, linalg.mat_mat(a, b))
        assert linalg.equal(izq, der)

    def test_traspuesta_dos_veces(self, gf2):
        m = [to_vec(v, 4) for v in (0b1011, 0b0110, 0b1111)]
        assert linalg.equal(linalg.transpose(linalg.transpose(m)), m)

    def test_x_mas_x_es_cero(self, gf2):
        v = to_vec(0xA5C, 12)
        assert linalg.is_zero(linalg.vec_add(v, v))

    def test_peso(self):
        assert linalg.weight(to_vec(0x000, 12)) == 0
        assert linalg.weight(to_vec(0xFFF, 12)) == 12
        assert linalg.weight(to_vec(0x98F, 12)) == 7

    def test_distancia(self):
        u, v = to_vec(0b1100, 4), to_vec(0b1010, 4)
        assert linalg.distance(u, v) == 2

    def test_hstack(self, gf2):
        izq = linalg.identity(2, gf2)
        der = [to_vec(0b10, 2), to_vec(0b11, 2)]
        assert [from_vec(f) for f in linalg.hstack(izq, der)] == [0b1010, 0b0111]

    def test_dimensiones_incompatibles(self, gf2):
        with pytest.raises(ValueError):
            linalg.vec_add([gf2(1)] * 3, [gf2(1)] * 2)
        with pytest.raises(ValueError):
            linalg.mat_mat([[gf2(1)] * 2], [[gf2(1)] * 2])
