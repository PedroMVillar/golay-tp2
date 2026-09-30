"""
Ejercicios 5 y 6. Chequeo que B, G y H cumplan las propiedades de la
Parte A, que el codificador dé las 4096 palabras con los pesos del
enunciado y que el decodificador resuelva r1, r2 y r3 igual que a mano.
También comparo el decodificador de cuatro casos con el de la tabla de
síndromes.
"""

import pytest

from golay import (B, B_ROWS, all_codewords, b_is_symmetric,
                   b_squared_is_identity, decode, decode_by_table, encode,
                   from_vec, g_h_are_orthogonal, minimum_distance, mult_b,
                   parity, popcount12, row_search, syndrome,
                   weight_distribution)
from golay import linalg
from conftest import (EJ1_CW, EJ1_MSG, EJ1_PARIDAD, EJ3_A_MANO,
                      EJ3_NO_CORREGIBLE, PESOS_ENUNCIADO)


class TestMatrices:

    def test_filas_de_b(self):
        assert [from_vec(f) for f in B] == list(B_ROWS)

    def test_b_simetrica(self):
        assert b_is_symmetric()

    def test_b_cuadrado_identidad(self):
        assert b_squared_is_identity()

    def test_g_por_h_traspuesta_cero(self):
        assert g_h_are_orthogonal()

    def test_filas_de_b_peso_siete(self):
        assert [linalg.weight(f) for f in B] == [7] * 12


class TestCodificador:

    def test_ejercicio_uno(self):
        assert parity(EJ1_MSG) == EJ1_PARIDAD
        assert encode(EJ1_MSG) == EJ1_CW

    def test_sistematico(self):
        for msg in (0x000, 0x001, 0xA5C, 0xFFF):
            assert encode(msg) >> 12 == msg

    def test_4096_palabras_distintas(self):
        assert len(set(all_codewords())) == 4096

    def test_sindrome_nulo_en_palabras_codigo(self):
        assert all(syndrome(cw) == 0 for cw in all_codewords())

    def test_distribucion_de_pesos(self):
        assert dict(weight_distribution()) == PESOS_ENUNCIADO

    def test_distancia_minima(self):
        assert minimum_distance() == 8

    def test_lineal(self):
        a, b = encode(0xA5C), encode(0x37F)
        assert syndrome(a ^ b) == 0


class TestSubmodulos:

    def test_mult_b_dos_veces(self):
        for v in (0x000, 0x001, 0x98F, 0xA5C, 0xFFF):
            assert mult_b(mult_b(v)) == v

    def test_popcount(self):
        for v in (0x000, 0x001, 0x98F, 0xA5C, 0xFFF):
            assert popcount12(v) == bin(v).count("1")

    def test_sindrome_como_en_el_rtl(self):
        # r·H^T tiene que coincidir con B·r[23:12] ^ r[11:0]
        for rx in (0x000000, 0xFFFFFF, EJ1_CW, 0xA5D9A6, 0x123456):
            assert syndrome(rx) == mult_b(rx >> 12) ^ (rx & 0xFFF)

    def test_row_search_gana_el_indice_menor(self):
        assert row_search(B_ROWS[0]) == (True, 0, 0)

    def test_row_search_sin_solucion(self):
        found, _, _ = row_search(0x7BC)   # el q de r_3
        assert not found


class TestDecodificador:

    def test_sin_error(self):
        res = decode(EJ1_CW)
        assert (res.msg, res.err, res.case) == (EJ1_MSG, 0, 1)
        assert not res.corrected and not res.uncorrectable

    @pytest.mark.parametrize("rx,sind,caso,err,msg", EJ3_A_MANO)
    def test_casos_de_la_parte_a(self, rx, sind, caso, err, msg):
        res = decode(rx)
        assert res.syndrome == sind
        assert res.case == caso
        assert res.err == err
        assert res.msg == msg
        assert res.corrected and not res.uncorrectable

    def test_no_corregible_de_la_parte_a(self):
        rx, sind = EJ3_NO_CORREGIBLE
        res = decode(rx)
        assert res.syndrome == sind
        assert res.case == 5
        assert res.uncorrectable and not res.corrected

    def test_errores_de_peso_uno(self):
        for bit in range(24):
            e = 1 << bit
            res = decode(EJ1_CW ^ e)
            assert res.err == e and res.msg == EJ1_MSG
            assert res.corrected and not res.uncorrectable

    def test_sindrome_no_depende_del_mensaje(self):
        e = 0x001003
        sindromes = {decode(encode(m) ^ e).syndrome for m in (0x000, 0xA5C, 0xFFF)}
        assert len(sindromes) == 1

    def test_decode_de_encode(self):
        for msg in (0x000, 0x001, 0xA5C, 0x800, 0xFFF):
            assert decode(encode(msg)).msg == msg


@pytest.mark.parametrize("rx", [
    EJ1_CW, 0xA5D9A6, 0xA5F9A4, 0xA5C9AA, 0x000000, 0xFFFFFF, 0x123456,
])
def test_coincide_con_la_tabla_de_sindromes(rx):
    a, b = decode(rx), decode_by_table(rx)
    assert a.uncorrectable == b.uncorrectable
    if not a.uncorrectable:
        assert (a.msg, a.err, a.corrected) == (b.msg, b.err, b.corrected)
