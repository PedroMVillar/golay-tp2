"""
golay: modelo de referencia del código de Golay extendido (24, 12).

Es la Parte B del Trabajo Práctico 2 del curso de FEC, y el golden model
contra el cual se verifica el RTL de la Parte C.

Todo el álgebra se apoya en :mod:`fec_algebra`, la librería de campos de
Galois del Trabajo Práctico 1, instanciada en ``GF(2^1)`` con
``P(x) = x + 1`` (o sea GF(2)). Sobre esa base este paquete agrega el
álgebra matricial que el trabajo anterior no cubría.

Uso básico::

    from golay import encode, decode

    v = encode(0xA5C)               # 0xA5C9A5
    r = v ^ 0x001003                # tres bits dados vuelta
    res = decode(r)
    res.msg              # 0xA5C
    res.err              # 0x001003
    res.case             # 2
    res.uncorrectable    # False

Mapa de módulos:

===================  ==========================================
:mod:`golay.bits`    convención de bits del enunciado
:mod:`golay.linalg`  álgebra matricial sobre GF(2^m)   (Ej. 4)
:mod:`golay.matrices`  B, G y H, y sus verificaciones  (Ej. 5)
:mod:`golay.encoder`   codificador y enumeración       (Ej. 5, 6)
:mod:`golay.decoder`   algoritmo de cuatro casos       (Ej. 6)
:mod:`golay.cosets`    tabla de síndromes (oráculo)    (Ej. 6)
:mod:`golay.stimulus`  estímulo para los TB de la Parte C (Ej. 7)
===================  ==========================================
"""

from .bits import (CW_BITS, GF2, MSG_BITS, PAR_BITS, from_vec, join_cw,
                   split_cw, to_vec, unit_int, unit_vec)
from .cosets import Coset, coset_table, decode_by_table, structure_summary
from .decoder import (DecodeResult, correct, decode, err_gen, mult_b,
                      popcount12, row_search, syndrome)
from .encoder import (all_codewords, encode, minimum_distance, parity,
                      weight_distribution)
from .matrices import (B_ROWS, b_is_symmetric, b_matrix,
                       b_squared_is_identity, check_all, g_h_are_orthogonal,
                       g_matrix, h_matrix, h_transpose)

__all__ = [
    # campo y convención de bits
    "GF2", "MSG_BITS", "PAR_BITS", "CW_BITS",
    "to_vec", "from_vec", "unit_vec", "unit_int", "split_cw", "join_cw",
    # matrices
    "B_ROWS", "b_matrix", "g_matrix", "h_matrix", "h_transpose",
    "b_is_symmetric", "b_squared_is_identity", "g_h_are_orthogonal", "check_all",
    # codificador
    "encode", "parity", "all_codewords", "weight_distribution",
    "minimum_distance",
    # decodificador
    "DecodeResult", "decode", "syndrome", "mult_b", "popcount12",
    "row_search", "err_gen", "correct",
    # tabla de síndromes
    "Coset", "coset_table", "decode_by_table", "structure_summary",
]
