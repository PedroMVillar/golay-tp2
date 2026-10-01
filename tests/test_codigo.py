"""
Ejercicios 5 y 6. Chequeo que B, G y H cumplan las propiedades de la
Parte A, que el codificador dé las 4096 palabras con los pesos del
enunciado y que el decodificador resuelva r1, r2 y r3 igual que a mano.
También comparo el decodificador de cuatro casos con el de la tabla de
síndromes.
"""

from golay import (b_is_symmetric, b_squared_is_identity, decode,
                   decode_by_table, encode, g_h_are_orthogonal,
                   minimum_distance, mult_b, syndrome, weight_distribution)


def test_propiedades_de_las_matrices():
    assert b_is_symmetric()
    assert b_squared_is_identity()
    assert g_h_are_orthogonal()


def test_codificar_a5c():
    # la cuenta a mano del Ejercicio 1
    assert encode(0xA5C) == 0xA5C9A5
    assert syndrome(0xA5C9A5) == 0


def test_distribucion_de_pesos():
    assert weight_distribution() == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
    assert minimum_distance() == 8


def test_sindrome_como_en_el_rtl():
    # r·H^T tiene que dar lo mismo que r[23:12]·B xor r[11:0]
    for r in (0x000000, 0xFFFFFF, 0xA5C9A5, 0xA5D9A6, 0x123456):
        assert syndrome(r) == mult_b(r >> 12) ^ (r & 0xFFF)


def test_r1():
    d = decode(0xA5D9A6)
    assert (d.syndrome, d.case, d.err, d.msg) == (0xEAA, 2, 0x001003, 0xA5C)
    assert d.corrected and not d.uncorrectable


def test_r2():
    d = decode(0xA5F9A4)
    assert (d.syndrome, d.case, d.err, d.msg) == (0x1B2, 4, 0x003001, 0xA5C)
    assert d.corrected and not d.uncorrectable


def test_r3_no_se_puede_corregir():
    d = decode(0xA5C9AA)
    assert d.syndrome == 0x00F
    assert d.case == 5
    assert d.uncorrectable


def test_palabra_sin_error():
    d = decode(0xA5C9A5)
    assert d.msg == 0xA5C and d.err == 0
    assert not d.corrected


def test_corrige_cualquier_error_de_un_bit():
    for bit in range(24):
        d = decode(0xA5C9A5 ^ (1 << bit))
        assert d.msg == 0xA5C and d.err == 1 << bit


def test_igual_que_la_tabla_de_sindromes():
    for r in (0xA5C9A5, 0xA5D9A6, 0xA5F9A4, 0xA5C9AA, 0x123456):
        a, b = decode(r), decode_by_table(r)
        assert a.uncorrectable == b.uncorrectable
        if not a.uncorrectable:
            assert (a.msg, a.err) == (b.msg, b.err)
