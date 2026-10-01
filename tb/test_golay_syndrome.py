# Primero paso las 4096 palabras código: como no tienen errores, el
# sindrome tiene que dar cero siempre. Dps paso una palabra con
# errores de 1, 2 y 3 bits, y ahí el síndrome tiene que coincidir con el
# que calcula el modelo.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import syndrome_vectors


@cocotb.test()
async def test_syndrome(dut):
    for vec in syndrome_vectors():
        dut.i_rx.value = vec["i_rx"]
        # el módulo no tiene reloj, así que espero un toque a que calcule la salida
        await Timer(1, "ns")
        syn = int(dut.o_syn.value)
        assert syn == vec["o_syn"], f"i_rx={vec['i_rx']:06X}"
        if vec["_zero"]:
            assert syn == 0
