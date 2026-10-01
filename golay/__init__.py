"""
Modelo de referencia del código de Golay extendido (24,12), Parte B del TP2.
"""

from .bits import GF2, MSG_BITS, PAR_BITS, from_vec, to_vec
from .sindromes import syndrome_table, decode_by_table, structure_summary
from .decoder import (DecodeResult, correct, decode, err_gen, mult_b,
                      popcount12, row_search, syndrome)
from .encoder import all_codewords, encode, minimum_distance, weight_distribution
from .matrices import (B, B_ROWS, G, H, HT, b_is_symmetric,
                       b_squared_is_identity, g_h_are_orthogonal)
