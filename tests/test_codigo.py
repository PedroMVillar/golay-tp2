"""
Ejercicios 5 y 6: matrices, codificador y decodificador.

Los valores esperados vienen del enunciado y de las cuentas a mano de la
Parte A del informe, no del propio modelo.
"""

import pytest

from golay import (B_ROWS, MSG_BITS, all_codewords, b_matrix, check_all,
                   decode, decode_by_table, encode, from_vec, minimum_distance,
                   mult_b, parity, popcount12, row_search, syndrome,
                   weight_distribution)
from golay import linalg
from conftest import (EJ1_CW, EJ1_MSG, EJ1_PARIDAD, EJ3_A_MANO,
                      EJ3_NO_CORREGIBLE, PESOS_ENUNCIADO)


class TestMatrices:
    """Ejercicio 5: construcción y verificación de G y H."""

    def test_las_filas_de_b_son_las_del_enunciado(self):
        filas = [from_vec(list(f)) for f in b_matrix()]
        assert filas == list(B_ROWS)

    def test_b_es_simetrica(self):
        assert check_all()["B = B^T"]

    def test_b_al_cuadrado_es_la_identidad(self):
        assert check_all()["B^2 = I"]

    def test_g_por_h_traspuesta_es_cero(self):
        assert check_all()["G H^T = 0"]

    def test_todas_las_filas_de_b_tienen_peso_impar(self):
        """La diagonal de B^2 sale de acá: w(b_i) = 7 para las doce filas."""
        pesos = [linalg.weight(list(f)) for f in b_matrix()]
        assert pesos == [7] * 12


class TestCodificador:
    """Ejercicio 5 y 6: el codificador matricial."""

    def test_caso_del_ejercicio_uno(self):
        """m = 0xA5C -> v = 0xA5C9A5, la cuenta a mano de la Parte A."""
        assert parity(EJ1_MSG) == EJ1_PARIDAD
        assert encode(EJ1_MSG) == EJ1_CW

    def test_la_palabra_lleva_el_mensaje_sin_tocar(self):
        """Es un código sistemático: cw[23:12] es el mensaje."""
        for msg in (0x000, 0x001, 0xA5C, 0xFFF):
            assert encode(msg) >> 12 == msg

    def test_hay_4096_palabras_distintas(self):
        assert len(set(all_codewords())) == 1 << MSG_BITS

    def test_toda_palabra_codigo_tiene_sindrome_nulo(self):
        assert all(syndrome(cw) == 0 for cw in all_codewords())

    def test_distribucion_de_pesos(self):
        """Ejercicio 5 contra la tabla del Ejercicio 2."""
        assert dict(weight_distribution()) == PESOS_ENUNCIADO

    def test_distancia_minima(self):
        assert minimum_distance() == 8

    def test_el_codigo_es_lineal(self):
        """La suma de dos palabras código es una palabra código."""
        a, b = encode(0xA5C), encode(0x37F)
        assert syndrome(a ^ b) == 0


class TestSubmodulos:
    """Las funciones que espejan los submódulos del RTL."""

    def test_mult_b_es_involutiva(self):
        """Aplicar B dos veces devuelve la entrada: es B^2 = I en acción."""
        for v in (0x000, 0x001, 0x98F, 0xA5C, 0xFFF):
            assert mult_b(mult_b(v)) == v

    def test_popcount_coincide_con_el_conteo_de_bits(self):
        for v in (0x000, 0x001, 0x98F, 0xA5C, 0xFFF):
            assert popcount12(v) == bin(v).count("1")

    def test_sindrome_matricial_igual_al_descompuesto(self):
        """s = r·H^T tiene que dar lo mismo que B·r[23:12] ⊕ r[11:0].

        Es la forma que implementa el RTL; si divergen, el golden model no
        sirve para verificar la Parte C.
        """
        for rx in (0x000000, 0xFFFFFF, EJ1_CW, 0xA5D9A6, 0x123456):
            assert syndrome(rx) == mult_b(rx >> 12) ^ (rx & 0xFFF)

    def test_row_search_resuelve_empates_por_indice_menor(self):
        """Con vec = b_0, el candidato i = 0 da peso 0 y tiene que ganar."""
        found, idx, res = row_search(B_ROWS[0])
        assert (found, idx, res) == (True, 0, 0)

    def test_row_search_sin_solucion(self):
        """Un vector lejos de todas las filas no encuentra candidato."""
        found, _, _ = row_search(0x7BC)   # el q de r_3, de la Parte A
        assert not found


class TestDecodificador:
    """Ejercicio 6: el algoritmo de cuatro casos."""

    def test_palabra_sin_error_no_se_corrige(self):
        res = decode(EJ1_CW)
        assert (res.msg, res.err, res.case) == (EJ1_MSG, 0, 1)
        assert not res.corrected and not res.uncorrectable

    @pytest.mark.parametrize("rx,sind,caso,err,msg", EJ3_A_MANO)
    def test_casos_resueltos_a_mano_en_la_parte_a(self, rx, sind, caso, err, msg):
        res = decode(rx)
        assert res.syndrome == sind
        assert res.case == caso
        assert res.err == err
        assert res.msg == msg
        assert res.corrected and not res.uncorrectable

    def test_caso_no_corregible_de_la_parte_a(self):
        rx, sind = EJ3_NO_CORREGIBLE
        res = decode(rx)
        assert res.syndrome == sind
        assert res.case == 5
        assert res.uncorrectable and not res.corrected

    def test_corrige_todos_los_errores_de_peso_uno(self):
        """Los 24 patrones de peso 1 sobre la palabra de referencia."""
        for bit in range(24):
            e = 1 << bit
            res = decode(EJ1_CW ^ e)
            assert res.err == e and res.msg == EJ1_MSG
            assert res.corrected and not res.uncorrectable

    def test_el_sindrome_no_depende_del_mensaje(self):
        """Pregunta del informe: s solo depende de e, no de v.

        La misma e sobre palabras código distintas da el mismo síndrome.
        """
        e = 0x001003
        sindromes = {decode(encode(m) ^ e).syndrome for m in (0x000, 0xA5C, 0xFFF)}
        assert len(sindromes) == 1

    def test_decodificar_es_inverso_de_codificar(self):
        for msg in (0x000, 0x001, 0xA5C, 0x800, 0xFFF):
            assert decode(encode(msg)).msg == msg


class TestOraculo:
    """El decodificador por tabla de síndromes valida al de cuatro casos."""

    @pytest.mark.parametrize("rx", [
        EJ1_CW, 0xA5D9A6, 0xA5F9A4, 0xA5C9AA, 0x000000, 0xFFFFFF, 0x123456,
    ])
    def test_ambos_decodificadores_coinciden(self, rx):
        a, b = decode(rx), decode_by_table(rx)
        assert a.uncorrectable == b.uncorrectable
        if not a.uncorrectable:
            assert (a.msg, a.err, a.corrected) == (b.msg, b.err, b.corrected)
