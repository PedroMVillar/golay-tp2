"""
Generadores de estímulo para los testbenches de la Parte C (Ejercicio 7b).

No se emiten archivos de vectores. Los testbenches de cocotb importan
este módulo y generan el estímulo adentro del propio test, que es el
patrón que usa la cátedra en la Unidad 3: el ``Makefile`` pone el modelo
en el ``PYTHONPATH`` y el testbench compara el DUT contra la función de
referencia ciclo a ciclo.

Formato
-------
Cada generador produce **diccionarios cuyas claves son exactamente los
nombres de los puertos** del módulo RTL correspondiente. Las claves que
empiezan con ``_`` son metadatos para el reporte y no son puertos.

Así, un testbench se escribe sin traducir nada::

    from golay.stimulus import mult_b_vectors

    for vec in mult_b_vectors():
        dut.i_vec.value = vec["i_vec"]
        await Timer(2, "ns")
        assert int(dut.o_vec.value) == vec["o_vec"]

Cobertura
---------
Los submódulos de 12 bits se barren exhaustivamente (4096 casos cada uno),
que es lo que pide el Ejercicio 10. El decodificador completo no se puede
barrer: hay 2^24 = 16,7 M palabras recibidas posibles. Para ese se cura un
conjunto que cubre las cinco ramas del algoritmo; ver
:func:`decoder_vectors`.
"""

from collections import Counter
from itertools import combinations

from fec_algebra import GF

from . import decoder
from .bits import CW_BITS, GF2, MSG_BITS, PAR_BITS
from .encoder import all_codewords, encode

#: Mensaje de referencia del enunciado, el del Ejercicio 1.
MSG_REF = 0xA5C

#: Cuántas palabras código extra se usan en el barrido de errores del
#: decodificador, además de la de referencia.
EXTRA_CODEWORDS = (0x000, 0xFFF, 0x001, 0x800)


# ------------------------------------------------- submódulos de 12 bits
def mult_b_vectors(field: GF = GF2):
    """``golay_mult_b``: barrido exhaustivo de los 4096 vectores.

    Incluye ``_o_vec_twice``, que es B aplicada dos veces. El testbench
    debe verificar que vuelve a ``i_vec``: es la comprobación en hardware
    de ``B^2 = I`` que pide el Ejercicio 10.
    """
    for v in range(1 << PAR_BITS):
        once = decoder.mult_b(v, field)
        yield {
            "i_vec": v,
            "o_vec": once,
            "_o_vec_twice": decoder.mult_b(once, field),
        }


def popcount12_vectors(field: GF = GF2):
    """``popcount12``: barrido exhaustivo de los 4096 vectores."""
    for v in range(1 << PAR_BITS):
        yield {"i_vec": v, "o_weight": decoder.popcount12(v, field)}


def row_search_vectors(field: GF = GF2):
    """``golay_row_search``: barrido exhaustivo de los 4096 vectores.

    Cuando ``o_found`` es 0, ``o_idx`` y ``o_res`` son don't-care: el
    testbench no los debe comparar.
    """
    for v in range(1 << PAR_BITS):
        found, idx, res = decoder.row_search(v, field)
        yield {
            "i_vec": v,
            "o_found": int(found),
            "o_idx": idx,
            "o_res": res,
        }


# ------------------------------------------------------ codificador
def encoder_vectors(field: GF = GF2):
    """``golay_encoder``: barrido exhaustivo de los 4096 mensajes."""
    for msg in range(1 << MSG_BITS):
        yield {"i_msg": msg, "o_cw": encode(msg, field)}


# -------------------------------------------------------- síndrome
def syndrome_vectors(field: GF = GF2):
    """``golay_syndrome``: las 4096 palabras código más errores dirigidos.

    Las palabras código tienen que dar síndrome nulo (Ejercicio 10). Los
    casos con error dan síndrome no nulo y ejercitan el camino de la
    matriz B dentro del módulo.
    """
    for cw in all_codewords(field):
        yield {"i_rx": cw, "o_syn": decoder.syndrome(cw, field), "_zero": True}

    base = encode(MSG_REF, field)
    for e in _patterns_up_to(3):
        rx = base ^ e
        yield {"i_rx": rx, "o_syn": decoder.syndrome(rx, field), "_zero": False}


# --------------------------------------------------- generador de error
def err_gen_vectors(field: GF = GF2):
    """``golay_err_gen``: entradas derivadas de casos reales del decodificador.

    Las diez entradas de este módulo no son independientes entre sí (las
    produce el pipeline aguas arriba), así que inventar combinaciones al
    azar generaría estados imposibles. En vez de eso se recorren las
    palabras recibidas de :func:`decoder_vectors`, se calculan los
    intermedios y se emite lo que le llegaría al módulo.
    """
    for caso in decoder_vectors(field):
        rx = caso["i_rx"]
        syn = decoder.syndrome(rx, field)
        q = decoder.mult_b(syn, field)
        found_syn, idx_syn, res_syn = decoder.row_search(syn, field)
        found_q, idx_q, res_q = decoder.row_search(q, field)
        err, unc, case = decoder.err_gen(
            syn, q, res_syn, res_q,
            decoder.popcount12(syn, field), decoder.popcount12(q, field),
            idx_syn, idx_q, found_syn, found_q,
        )
        yield {
            "i_syn": syn, "i_q": q,
            "i_res_syn": res_syn, "i_res_q": res_q,
            "i_w_syn": decoder.popcount12(syn, field),
            "i_w_q": decoder.popcount12(q, field),
            "i_idx_syn": idx_syn, "i_idx_q": idx_q,
            "i_found_syn": int(found_syn), "i_found_q": int(found_q),
            "o_err": err, "o_uncorrectable": int(unc),
            "_case": case,
        }


# ------------------------------------------------ decodificador completo
def _patterns_up_to(max_weight: int):
    """Patrones de error de 24 bits de peso 1..max_weight."""
    for w in range(1, max_weight + 1):
        for pos in combinations(range(CW_BITS), w):
            e = 0
            for p in pos:
                e |= 1 << p
            yield e


def decoder_vectors(field: GF = GF2, weight4_stride: int = 97):
    """``golay_decoder``: conjunto curado que cubre las cinco ramas.

    No se puede barrer el espacio de 2^24 palabras recibidas, así que se
    arma esto:

    1. Las 4096 palabras código sin error. Síndrome nulo, rama 1,
       ``o_corrected`` en bajo. Es el chequeo del Ejercicio 10.
    2. Todos los patrones de peso 1, 2 y 3 (2325) aplicados a la palabra
       de referencia y a cuatro palabras más. Estos son los corregibles y
       recorren las ramas 1 a 4.
    3. Patrones de peso 4, submuestreados con paso ``weight4_stride``,
       sobre la palabra de referencia. Todos caen en la rama 5.

    Use :func:`branch_coverage` para confirmar que las cinco ramas
    quedaron cubiertas.
    """
    palabras = (encode(MSG_REF, field),) + tuple(
        encode(m, field) for m in EXTRA_CODEWORDS
    )

    for cw in all_codewords(field):
        yield _decoder_record(cw, field)

    for cw in palabras:
        for e in _patterns_up_to(3):
            yield _decoder_record(cw, field, expected_err=e)

    base = palabras[0]
    for k, pos in enumerate(combinations(range(CW_BITS), 4)):
        if k % weight4_stride:
            continue
        e = 0
        for p in pos:
            e |= 1 << p
        yield _decoder_record(base, field, expected_err=e)


def _decoder_record(cw: int, field: GF, expected_err: int = 0) -> dict:
    """Arma el registro de un caso del decodificador completo."""
    rx = cw ^ expected_err
    res = decoder.decode(rx, field)
    return {
        "i_rx": rx,
        "o_msg": res.msg,
        "o_err": res.err,
        "o_corrected": int(res.corrected),
        "o_uncorrectable": int(res.uncorrectable),
        "_case": res.case,
        "_syndrome": res.syndrome,
        "_sent_cw": cw,
        "_sent_err": expected_err,
        "_exact": (not res.uncorrectable) and res.err == expected_err,
    }


def branch_coverage(vectors) -> Counter:
    """Cuenta cuántos casos cayó en cada rama del algoritmo."""
    return Counter(v["_case"] for v in vectors)
