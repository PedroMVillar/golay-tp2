"""
Decodificador de cuatro casos.

Hay una función por cada submódulo del RTL de la Parte C (mult_b,
popcount12, syndrome, row_search, err_gen, correct) y decode() las
encadena en el mismo orden que el pipeline.
"""

from dataclasses import dataclass

from . import linalg
from .bits import from_vec, join_cw, split_cw, to_vec, unit_int
from .matrices import B, HT


@dataclass
class DecodeResult:
    msg: int
    err: int
    corrected: bool
    uncorrectable: bool
    syndrome: int
    case: int


def mult_b(vec):
    return from_vec(linalg.vec_mat(to_vec(vec, 12), B))


def popcount12(vec):
    return linalg.weight(to_vec(vec, 12))


def syndrome(rx):
    return from_vec(linalg.vec_mat(to_vec(rx, 24), HT))


def row_search(vec):
    # primer i con w(vec ^ b_i) <= 2; si no hay, idx y res no importan
    v = to_vec(vec, 12)
    for i in range(12):
        cand = linalg.vec_add(v, B[i])
        if linalg.weight(cand) <= 2:
            return True, i, from_vec(cand)
    return False, 0, 0


def err_gen(syn, q, res_syn, res_q, w_syn, w_q,
            idx_syn, idx_q, found_syn, found_q):
    if w_syn <= 3:
        return join_cw(0, syn), False, 1
    if found_syn:
        return join_cw(unit_int(idx_syn), res_syn), False, 2
    if w_q <= 3:
        return join_cw(q, 0), False, 3
    if found_q:
        return join_cw(res_q, unit_int(idx_q)), False, 4
    return 0, True, 5


def correct(rx, err):
    cw = rx ^ err
    msg, _ = split_cw(cw)
    return cw, msg, err != 0


def decode(rx):
    syn = syndrome(rx)
    q = mult_b(syn)
    found_syn, idx_syn, res_syn = row_search(syn)
    found_q, idx_q, res_q = row_search(q)

    err, uncorrectable, case = err_gen(
        syn, q, res_syn, res_q, popcount12(syn), popcount12(q),
        idx_syn, idx_q, found_syn, found_q,
    )
    if uncorrectable:
        return DecodeResult(0, 0, False, True, syn, case)

    _, msg, corrected = correct(rx, err)
    return DecodeResult(msg, err, corrected, False, syn, case)
