"""
Excepciones propias de fec_algebra.

Podría usar ValueError y ZeroDivisionError de Python directamente, pero
así queda más claro qué se rompió exactamente (y quien use la librería
puede atajar cada caso por separado si quiere).
"""


class GFError(Exception):
    """Excepción base del paquete. Sirve para capturar cualquier error propio con un solo except GFError."""
    pass


class GFZeroDivisionError(GFError):
    """División por el elemento 0 del campo (o por el polinomio nulo), o intento de invertir el 0."""
    pass


class GFFieldMismatchError(GFError):
    """Se lanza al operar entre dos elementos o polinomios que no pertenecen al mismo campo, por ejemplo sumar algo de GF(2^8) con algo de GF(2^4). No tiene sentido matemático, así que se corta ahí."""
    pass


class GFValueError(GFError):
    """Valor fuera de lo esperado para el campo: un entero fuera de rango, un m inválido, un primitive_poly mal formado, o un coeficiente de GFPoly que no es un elemento válido."""
    pass
