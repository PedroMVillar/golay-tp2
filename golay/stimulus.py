"""
Estímulo para los testbenches de cocotb de la Parte C (Ejercicio 7b).

Cada generador devuelve diccionarios cuyas claves son los nombres de los
puertos del módulo RTL. Las claves con _ adelante son datos extra para
el reporte, no puertos.
"""

from collections import Counter

from . import decoder
from .sindromes import error_patterns
from .encoder import all_codewords, encode

MSG_REF = 0xA5C
EXTRA_MSGS = (0x000, 0xFFF, 0x001, 0x800)


def mult_b_vectors():
    for v in range(4096):
        yield {"i_vec": v, "o_vec": decoder.mult_b(v)}


def popcount12_vectors():
    for v in range(4096):
        yield {"i_vec": v, "o_weight": decoder.popcount12(v)}


def row_search_vectors():
    for v in range(4096):
        found, idx, res = decoder.row_search(v)
        yield {"i_vec": v, "o_found": int(found), "o_idx": idx, "o_res": res}


def encoder_vectors():
    for msg in range(4096):
        yield {"i_msg": msg, "o_cw": encode(msg)}


def syndrome_vectors():
    for cw in all_codewords():
        yield {"i_rx": cw, "o_syn": decoder.syndrome(cw), "_zero": True}

    base = encode(MSG_REF)
    for e in errors_up_to(3):
        rx = base ^ e
        yield {"i_rx": rx, "o_syn": decoder.syndrome(rx), "_zero": False}


def err_gen_vectors():
    # las entradas de err_gen salen de palabras recibidas reales, porque
    # combinarlas al azar da estados que el pipeline nunca produce
    for caso in decoder_vectors():
        syn = decoder.syndrome(caso["i_rx"])
        q = decoder.mult_b(syn)
        found_syn, idx_syn, res_syn = decoder.row_search(syn)
        found_q, idx_q, res_q = decoder.row_search(q)
        w_syn, w_q = decoder.popcount12(syn), decoder.popcount12(q)
        err, unc, case = decoder.err_gen(syn, q, res_syn, res_q, w_syn, w_q,
                                         idx_syn, idx_q, found_syn, found_q)
        yield {
            "i_syn": syn, "i_q": q,
            "i_res_syn": res_syn, "i_res_q": res_q,
            "i_w_syn": w_syn, "i_w_q": w_q,
            "i_idx_syn": idx_syn, "i_idx_q": idx_q,
            "i_found_syn": int(found_syn), "i_found_q": int(found_q),
            "o_err": err, "o_uncorrectable": int(unc),
            "_case": case,
        }


def correct_vectors():
    for caso in decoder_vectors():
        rx, err = caso["i_rx"], caso["o_err"]
        cw, msg, corrected = decoder.correct(rx, err)
        yield {"i_rx": rx, "i_err": err, "o_cw": cw, "o_msg": msg,
               "o_corrected": int(corrected)}


def errors_up_to(max_peso):
    for w in range(1, max_peso + 1):
        yield from error_patterns(w)


def decoder_vectors(paso_peso4=97):
    # 1) las 4096 palabras código sin error
    # 2) todos los errores de peso 1 a 3 sobre cinco palabras código
    # 3) una submuestra de errores de peso 4
    palabras = [encode(m) for m in (MSG_REF,) + EXTRA_MSGS]

    for cw in all_codewords():
        yield _decoder_record(cw)

    for cw in palabras:
        for e in errors_up_to(3):
            yield _decoder_record(cw, e)

    for k, e in enumerate(error_patterns(4)):
        if k % paso_peso4 == 0:
            yield _decoder_record(palabras[0], e)


def _decoder_record(cw, e=0):
    rx = cw ^ e
    res = decoder.decode(rx)
    return {
        "i_rx": rx,
        "o_msg": res.msg,
        "o_err": res.err,
        "o_corrected": int(res.corrected),
        "o_uncorrectable": int(res.uncorrectable),
        "_case": res.case,
    }


def branch_coverage(vectors):
    return Counter(v["_case"] for v in vectors)
