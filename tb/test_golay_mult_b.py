# Testbench de golay_mult_b: los 4096 vectores, y aplicarlo dos veces
# tiene que devolver la entrada (B^2 = I).

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import mult_b_vectors


@cocotb.test()
async def test_mult_b(dut):
    for vec in mult_b_vectors():
        dut.i_vec.value = vec["i_vec"]
        await Timer(1, "ns")
        salida = int(dut.o_vec.value)
        assert salida == vec["o_vec"], f"i_vec={vec['i_vec']:03X}"

        dut.i_vec.value = salida
        await Timer(1, "ns")
        assert int(dut.o_vec.value) == vec["i_vec"], f"B^2 != I en {vec['i_vec']:03X}"
