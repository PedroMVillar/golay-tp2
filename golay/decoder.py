"""
Decodificador de referencia: el algoritmo de cuatro casos de la Parte C.

Las funciones de este módulo están a propósito en correspondencia uno a
uno con los submódulos del RTL, con los mismos nombres y las mismas
entradas y salidas:

======================  =========================
RTL (Parte C)           referencia (acá)
======================  =========================
``golay_mult_b``        :func:`mult_b`
``popcount12``          :func:`popcount12`
``golay_syndrome``      :func:`syndrome`
``golay_row_search``    :func:`row_search`
``golay_err_gen``       :func:`err_gen`
``golay_correct``       :func:`correct`
======================  =========================

:func:`decode` no reimplementa nada: compone esas seis, igual que el
``golay_decoder`` compone sus submódulos. Así el testbench de cada
submódulo compara contra la función homónima, y el de integración compara
contra :func:`decode`.

Nota sobre el síndrome
----------------------
El Ejercicio 9 del enunciado escribe ``s = r[23:12] ⊕ B·r[11:0]``, pero
esa expresión intercambia los dos bloques y es inconsistente con la tabla
de casos: con ella el caso 1 pediría ``e_2 = s·B`` en lugar de ``e_2 = s``,
y los conteos del Ejercicio 7a no dan. Acá se usa ``s = H·r^T``, o sea
``B·r[23:12] ⊕ r[11:0]``, que es la que sale del ``H = [B | I_12]``
definido en la portada del propio enunciado y la que reproduce esos
conteos.
"""

from dataclasses import dataclass

from fec_algebra import GF

from . import linalg
from .bits import (GF2, CW_BITS, PAR_BITS, from_vec, join_cw,
                   split_cw, to_vec, unit_int)
from .matrices import _as_lists, b_matrix, h_transpose

#: Umbral de peso del síndrome para los casos 1 y 3.
W_DIRECT = 3
#: Umbral de peso para que una fila b_i sirva en los casos 2 y 4.
W_ROW = 2


@dataclass(frozen=True)
class DecodeResult:
    """Lo que devuelve :func:`decode`.

    Attributes:
        msg: mensaje decodificado, 12 bits. Solo válido si no es
            ``uncorrectable``.
        err: patrón de error estimado, 24 bits. Solo válido si no es
            ``uncorrectable``.
        corrected: hubo corrección, o sea ``err != 0``. Es lo que puede
            saber el ``golay_correct`` del RTL, que solo recibe ``i_rx``
            e ``i_err``.
        uncorrectable: se llegó al caso 5. Con esta bandera en alto,
            ``msg`` y ``err`` no son válidas.
        syndrome: el síndrome ``s``, 12 bits. No lo pide el Ejercicio 6,
            pero el testbench de integración lo necesita para espiar la
            salida de ``golay_syndrome``.
        case: qué rama resolvió, de 1 a 5.
    """

    msg: int
    err: int
    corrected: bool
    uncorrectable: bool
    syndrome: int
    case: int


# ------------------------------------------------ submódulos de la Parte C
def mult_b(vec: int, field: GF = GF2) -> int:
    """``golay_mult_b``: multiplica un vector de 12 bits por B.

    Es el único lugar del modelo donde se usa la matriz B, igual que en el
    RTL es el único módulo donde aparece.
    """
    v = to_vec(vec, PAR_BITS, field)
    return from_vec(linalg.vec_mat(v, _as_lists(b_matrix(field))))


def popcount12(vec: int, field: GF = GF2) -> int:
    """``popcount12``: peso de Hamming de un vector de 12 bits.

    Se calcula con :func:`golay.linalg.weight` sobre el vector de
    ``GFElement``, que es el peso que pide agregar el Ejercicio 4, y no
    con un ``bin().count('1')``.
    """
    return linalg.weight(to_vec(vec, PAR_BITS, field))


def syndrome(rx: int, field: GF = GF2) -> int:
    """``golay_syndrome``: síndrome de una palabra recibida, ``s = r · H^T``.

    Se calcula con el producto matricial completo contra ``H^T``. La forma
    descompuesta que implementa el RTL, ``B·r[23:12] ⊕ r[11:0]``, es
    equivalente y los tests verifican que coinciden para las 4096 palabras
    código y para una muestra de palabras arbitrarias.
    """
    v = to_vec(rx, CW_BITS, field)
    return from_vec(linalg.vec_mat(v, _as_lists(h_transpose(field))))


def row_search(vec: int, field: GF = GF2) -> tuple:
    """``golay_row_search``: busca una fila ``b_i`` que baje el peso a ≤ 2.

    Evalúa los doce candidatos ``vec ⊕ b_i`` y devuelve el primero cuyo
    peso no supere 2, resolviendo empates por prioridad de índice (gana el
    ``i`` más chico), que es lo que pide el Ejercicio 9.

    Returns:
        ``(found, idx, res)``. Si ``found`` es False, ``idx`` y ``res``
        valen 0 y el testbench debe tratarlos como don't-care: el RTL
        puede dejar cualquier cosa en esos puertos.
    """
    v = to_vec(vec, PAR_BITS, field)
    for i in range(PAR_BITS):
        cand = linalg.vec_add(v, list(b_matrix(field)[i]))
        if linalg.weight(cand) <= W_ROW:
            return True, i, from_vec(cand)
    return False, 0, 0


def err_gen(syn: int, q: int, res_syn: int, res_q: int,
            w_syn: int, w_q: int, idx_syn: int, idx_q: int,
            found_syn: bool, found_q: bool) -> tuple:
    """``golay_err_gen``: prioridad de los cuatro casos.

    Recibe exactamente lo mismo que el módulo del RTL (que ya viene todo
    calculado por las etapas anteriores del pipeline) y aplica la tabla:

    ====  =========================  ==========================
    caso  condición                  patrón de error
    ====  =========================  ==========================
    1     ``w(s) ≤ 3``               ``e = (0 | s)``
    2     ``∃i : w(s ⊕ b_i) ≤ 2``    ``e = (u_i | s ⊕ b_i)``
    3     ``w(q) ≤ 3``               ``e = (q | 0)``
    4     ``∃i : w(q ⊕ b_i) ≤ 2``    ``e = (q ⊕ b_i | u_i)``
    5     ninguna de las anteriores  ``o_uncorrectable``
    ====  =========================  ==========================

    Returns:
        ``(err, uncorrectable, case)``. El RTL solo expone los dos
        primeros; ``case`` se agrega para el informe y los tests.
    """
    if w_syn <= W_DIRECT:
        return join_cw(0, syn), False, 1
    if found_syn:
        return join_cw(unit_int(idx_syn), res_syn), False, 2
    if w_q <= W_DIRECT:
        return join_cw(q, 0), False, 3
    if found_q:
        return join_cw(res_q, unit_int(idx_q)), False, 4
    return 0, True, 5


def correct(rx: int, err: int) -> tuple:
    """``golay_correct``: aplica el patrón de error y extrae el mensaje.

    Returns:
        ``(cw, msg, corrected)``. ``corrected`` es ``err != 0``: es lo
        único deducible de ``i_rx`` e ``i_err``, que es todo lo que recibe
        el módulo del RTL.
    """
    cw = rx ^ err
    msg, _ = split_cw(cw)
    return cw, msg, err != 0


# --------------------------------------------------------- decodificador
def decode(rx: int, field: GF = GF2) -> DecodeResult:
    """Decodifica una palabra recibida de 24 bits.

    Compone los submódulos en el mismo orden que el pipeline de tres
    etapas de la Parte C:

    - E1: :func:`syndrome`
    - E2: :func:`popcount12`, :func:`mult_b` y :func:`row_search`, sobre
      ``s`` y sobre ``q = s · B``
    - E3: :func:`err_gen` y :func:`correct`

    Raises:
        ValueError: si rx no entra en 24 bits.
    """
    syn = syndrome(rx, field)                       # E1
    q = mult_b(syn, field)                          # E2
    w_syn, w_q = popcount12(syn, field), popcount12(q, field)
    found_syn, idx_syn, res_syn = row_search(syn, field)
    found_q, idx_q, res_q = row_search(q, field)

    err, uncorrectable, case = err_gen(              # E3
        syn, q, res_syn, res_q, w_syn, w_q,
        idx_syn, idx_q, found_syn, found_q,
    )
    if uncorrectable:
        return DecodeResult(msg=0, err=0, corrected=False, uncorrectable=True,
                            syndrome=syn, case=case)

    _, msg, corrected = correct(rx, err)
    return DecodeResult(msg=msg, err=err, corrected=corrected,
                        uncorrectable=False, syndrome=syn, case=case)
