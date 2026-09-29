# Testbench de golay_syndrome: las 4096 palabras código tienen que dar
# síndrome nulo, y además se prueban errores de peso 1 a 3.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import syndrome_vectors


@cocotb.test()
async def test_syndrome(dut):
    for vec in syndrome_vectors():
        dut.i_rx.value = vec["i_rx"]
        await Timer(1, "ns")
        syn = int(dut.o_syn.value)
        assert syn == vec["o_syn"], f"i_rx={vec['i_rx']:06X}"
        if vec["_zero"]:
            assert syn == 0
