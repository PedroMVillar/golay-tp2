"""
Ejercicio 4: la librería del TP1 con m = 1, y el álgebra matricial nueva.

La primera parte verifica que ``GF(m=1, P(x)=x+1)`` reduce efectivamente a
GF(2): las tablas de suma, producto e inverso se comparan contra las de
GF(2) escritas a mano. La segunda parte prueba el álgebra matricial que el
TP1 no cubría.
"""

import pytest

from fec_algebra import GF, GFZeroDivisionError
from golay import GF2, from_vec, to_vec
from golay import linalg


class TestGF2:
    """El campo GF(2^1) con P(x) = x + 1 se comporta como GF(2)."""

    def test_orden(self, gf2):
        assert gf2.order == 2
        assert gf2.m == 1

    @pytest.mark.parametrize("a,b,esperado", [
        (0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0),
    ])
    def test_tabla_de_suma(self, gf2, a, b, esperado):
        """En GF(2) sumar es XOR."""
        assert int(gf2(a) + gf2(b)) == esperado

    @pytest.mark.parametrize("a,b,esperado", [
        (0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1),
    ])
    def test_tabla_de_producto(self, gf2, a, b, esperado):
        """En GF(2) multiplicar es AND."""
        assert int(gf2(a) * gf2(b)) == esperado

    def test_inverso_del_uno(self, gf2):
        """El 1 es su propio inverso; es el único elemento invertible."""
        assert int(~gf2(1)) == 1

    def test_el_cero_no_tiene_inverso(self, gf2):
        with pytest.raises(GFZeroDivisionError):
            ~gf2(0)

    def test_no_hizo_falta_tocar_la_libreria(self):
        """La implementación del TP1 no asume m >= 2 en ningún lado.

        Este test documenta el hallazgo del Ejercicio 4: el campo se
        instancia con m = 1 sin ninguna modificación. Si alguien
        "optimiza" fec_algebra asumiendo m >= 2, esto lo detecta.
        """
        campo = GF(m=1, primitive_poly=0b1)
        assert campo == GF2
        assert [int(campo(v)) for v in range(campo.order)] == [0, 1]
        assert int(campo.power(1, 0)) == 1
        assert int(campo.divide(1, 1)) == 1


class TestConversionDeBits:
    """La convención del enunciado: v[i] es el bit (ancho-1-i)."""

    def test_el_elemento_cero_es_el_bit_mas_significativo(self):
        v = to_vec(0b100000000000, 12)
        assert int(v[0]) == 1
        assert all(int(x) == 0 for x in v[1:])

    def test_ida_y_vuelta(self):
        for valor in (0x000, 0x001, 0x98F, 0xA5C, 0xFFF):
            assert from_vec(to_vec(valor, 12)) == valor

    def test_ancho_invalido(self):
        with pytest.raises(ValueError):
            to_vec(0x1000, 12)   # no entra en 12 bits


class TestLinalg:
    """El álgebra matricial agregada en el Ejercicio 4."""

    def test_identidad_es_neutro(self, gf2):
        ident = linalg.identity(4, gf2)
        m = [to_vec(v, 4) for v in (0b1011, 0b0110, 0b1111, 0b0001)]
        assert linalg.equal(linalg.mat_mat(m, ident), m)
        assert linalg.equal(linalg.mat_mat(ident, m), m)

    def test_vec_mat_selecciona_filas(self, gf2):
        """En GF(2), v·M es la suma de las filas donde v tiene un 1."""
        m = [to_vec(v, 4) for v in (0b1000, 0b0100, 0b0010, 0b0001)]
        v = to_vec(0b1010, 4)
        assert from_vec(linalg.vec_mat(v, m)) == 0b1010

    def test_vec_mat_contra_cuenta_a_mano(self, gf2):
        """Un producto chico verificado a mano.

        M = [[1,1],[0,1]],  v = [1,1]  ->  v·M = [1, 1+1] = [1, 0]
        """
        m = [[gf2(1), gf2(1)], [gf2(0), gf2(1)]]
        v = [gf2(1), gf2(1)]
        assert [int(x) for x in linalg.vec_mat(v, m)] == [1, 0]

    def test_mat_mat_es_asociativo_con_vec_mat(self, gf2):
        a = [to_vec(v, 3) for v in (0b101, 0b011, 0b110)]
        b = [to_vec(v, 3) for v in (0b001, 0b111, 0b010)]
        v = to_vec(0b101, 3)
        izq = linalg.vec_mat(linalg.vec_mat(v, a), b)
        der = linalg.vec_mat(v, linalg.mat_mat(a, b))
        assert linalg.equal(izq, der)

    def test_traspuesta_es_involutiva(self, gf2):
        m = [to_vec(v, 4) for v in (0b1011, 0b0110, 0b1111)]
        assert linalg.equal(linalg.transpose(linalg.transpose(m)), m)

    def test_suma_es_su_propia_inversa(self, gf2):
        """En característica 2, x + x = 0."""
        v = to_vec(0xA5C, 12)
        assert linalg.is_zero(linalg.vec_add(v, v))

    def test_peso_de_hamming(self):
        assert linalg.weight(to_vec(0x000, 12)) == 0
        assert linalg.weight(to_vec(0xFFF, 12)) == 12
        assert linalg.weight(to_vec(0x98F, 12)) == 7   # b_0, cuenta de la Parte A

    def test_distancia_es_peso_de_la_diferencia(self):
        u, v = to_vec(0b1100, 4), to_vec(0b1010, 4)
        assert linalg.distance(u, v) == 2

    def test_hstack(self, gf2):
        izq = linalg.identity(2, gf2)
        der = [to_vec(0b10, 2), to_vec(0b11, 2)]
        assert [from_vec(f) for f in linalg.hstack(izq, der)] == [0b1010, 0b0111]

    @pytest.mark.parametrize("op,args", [
        (linalg.vec_add, ([1, 2, 3], [1, 2])),
        (linalg.mat_mat, ([[1, 2]], [[1, 2]])),
    ])
    def test_dimensiones_incompatibles_fallan(self, gf2, op, args):
        a, b = args
        a = [gf2(1)] * len(a) if not isinstance(a[0], list) else [[gf2(1)] * len(f) for f in a]
        b = [gf2(1)] * len(b) if not isinstance(b[0], list) else [[gf2(1)] * len(f) for f in b]
        with pytest.raises(ValueError):
            op(a, b)
