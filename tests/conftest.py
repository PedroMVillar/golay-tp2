"""
Valores de referencia sacados del enunciado y de las cuentas de la Parte A.
"""

import pytest

from golay import GF2

PESOS_ENUNCIADO = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}

# (recibida, síndrome, caso, error, mensaje)
EJ3_A_MANO = [
    (0xA5D9A6, 0xEAA, 2, 0x001003, 0xA5C),
    (0xA5F9A4, 0x1B2, 4, 0x003001, 0xA5C),
]
EJ3_NO_CORREGIBLE = (0xA5C9AA, 0x00F)

EJ1_MSG, EJ1_PARIDAD, EJ1_CW = 0xA5C, 0x9A5, 0xA5C9A5


@pytest.fixture
def gf2():
    return GF2
