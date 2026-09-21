"""
Fixtures y datos de referencia compartidos por los tests del modelo.

Los valores esperados salen de dos lugares independientes del código:
las tablas del enunciado y las cuentas a mano de la Parte A del informe.
Ningún test compara el modelo solamente contra sí mismo.
"""

import pytest

from golay import GF2

#: Distribución de pesos del código, dato del enunciado (Ejercicio 2).
PESOS_ENUNCIADO = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}

#: Tabla del Ejercicio 7a: (peso de e) -> (patrones, corregidos, detectados).
EJ7A_ENUNCIADO = {
    0: (1, 1, 0),
    1: (24, 24, 0),
    2: (276, 276, 0),
    3: (2024, 2024, 0),
    4: (10626, 0, 10626),
}

#: Casos resueltos a mano en la Parte A del informe (Ejercicio 3).
#: (recibida, síndrome, caso, patrón de error, mensaje)
EJ3_A_MANO = [
    (0xA5D9A6, 0xEAA, 2, 0x001003, 0xA5C),
    (0xA5F9A4, 0x1B2, 4, 0x003001, 0xA5C),
]

#: La palabra recibida del Ejercicio 3 que no es corregible (error de peso 4).
EJ3_NO_CORREGIBLE = (0xA5C9AA, 0x00F)

#: Mensaje y palabra código del Ejercicio 1.
EJ1_MSG, EJ1_PARIDAD, EJ1_CW = 0xA5C, 0x9A5, 0xA5C9A5


@pytest.fixture
def gf2():
    """El campo del TP: GF(2^1) con P(x) = x + 1."""
    return GF2
