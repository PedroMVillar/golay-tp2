"""
Convención de bits del enunciado, en un solo lugar.

El TP fija que ``cw[23:12]`` es el mensaje y ``cw[11:0]`` la paridad, que
el bit ``m[11-i]`` es ``m_i``, y que el bit ``[11-j]`` de ``b_i`` es
``B[i][j]``. O sea: **el elemento 0 de un vector es el bit más
significativo del entero**.

Todo el modelo entra y sale en enteros (los testbenches de cocotb hablan
enteros, el enunciado tabula en hexa) pero opera internamente con
vectores de ``GFElement``. La traducción entre esos dos mundos pasa
exclusivamente por este módulo.

Que esté acá y en ningún otro lado no es prolijidad: un desajuste de
convención no rompe nada ruidosamente, devuelve números plausibles y
equivocados. Es la clase de error que hay que hacer imposible, no
detectable.
"""

from fec_algebra import GF

#: El campo del TP: GF(2^1) con P(x) = x + 1, o sea GF(2) a secas.
GF2 = GF(m=1, primitive_poly=0b1)

MSG_BITS = 12   #: bits de mensaje, cw[23:12]
PAR_BITS = 12   #: bits de paridad, cw[11:0]
CW_BITS = MSG_BITS + PAR_BITS   #: largo de la palabra código


def to_vec(value: int, width: int, field: GF = GF2) -> list:
    """Entero -> vector de GFElement, con ``v[i]`` = bit ``width-1-i``.

    Args:
        value: entero a descomponer, en ``[0, 2^width)``.
        width: cantidad de bits (y largo del vector resultante).
        field: campo de los coeficientes; por defecto GF(2).

    Raises:
        ValueError: si width no es positivo o value no entra en width bits.
    """
    if width <= 0:
        raise ValueError(f"width debe ser positivo, se recibió {width!r}")
    if not isinstance(value, int) or not (0 <= value < (1 << width)):
        raise ValueError(
            f"value debe ser un entero en [0, {(1 << width) - 1}] "
            f"({width} bits), se recibió {value!r}"
        )
    return [field((value >> (width - 1 - i)) & 1) for i in range(width)]


def from_vec(vec: list) -> int:
    """Vector de GFElement -> entero. Inversa exacta de :func:`to_vec`.

    Raises:
        ValueError: si el vector está vacío.
    """
    if not vec:
        raise ValueError("El vector no puede estar vacío.")
    width = len(vec)
    out = 0
    for i, coef in enumerate(vec):
        if int(coef):
            out |= 1 << (width - 1 - i)
    return out


def unit_vec(i: int, width: int = MSG_BITS, field: GF = GF2) -> list:
    """El vector ``u_i``: todo ceros menos un uno en la posición ``i``.

    Es el que aparece en los casos 2 y 4 del algoritmo de decodificación.

    Raises:
        ValueError: si i cae fuera de [0, width).
    """
    if not (0 <= i < width):
        raise ValueError(f"i debe estar en [0, {width}), se recibió {i!r}")
    return [field(1 if j == i else 0) for j in range(width)]


def unit_int(i: int, width: int = MSG_BITS) -> int:
    """Lo mismo que :func:`unit_vec` pero como entero: ``1 << (width-1-i)``."""
    if not (0 <= i < width):
        raise ValueError(f"i debe estar en [0, {width}), se recibió {i!r}")
    return 1 << (width - 1 - i)


def split_cw(cw: int) -> tuple:
    """Parte una palabra de 24 bits en ``(mensaje, paridad)``.

    Raises:
        ValueError: si cw no entra en 24 bits.
    """
    if not isinstance(cw, int) or not (0 <= cw < (1 << CW_BITS)):
        raise ValueError(
            f"cw debe ser un entero de {CW_BITS} bits, se recibió {cw!r}"
        )
    return cw >> PAR_BITS, cw & ((1 << PAR_BITS) - 1)


def join_cw(msg: int, par: int) -> int:
    """Arma una palabra de 24 bits a partir de mensaje y paridad.

    Raises:
        ValueError: si alguna de las dos mitades no entra en 12 bits.
    """
    if not (0 <= msg < (1 << MSG_BITS)):
        raise ValueError(f"msg debe entrar en {MSG_BITS} bits, se recibió {msg!r}")
    if not (0 <= par < (1 << PAR_BITS)):
        raise ValueError(f"par debe entrar en {PAR_BITS} bits, se recibió {par!r}")
    return (msg << PAR_BITS) | par


def popcount(value: int) -> int:
    """Peso de Hamming de un entero, para cuando no hace falta vectorizar.

    El peso "oficial" del modelo es :func:`golay.linalg.weight`, que opera
    sobre vectores de GFElement como pide el Ejercicio 4. Este es el atajo
    para los generadores de estímulo y los chequeos rápidos, y los tests
    verifican que los dos coinciden.
    """
    return bin(value).count("1")
