# Testbench de popcount12: barrido de los 4096 vectores.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import popcount12_vectors


@cocotb.test()
async def test_popcount12(dut):
    for vec in popcount12_vectors():
        dut.i_vec.value = vec["i_vec"]
        await Timer(1, "ns")
        assert int(dut.o_weight.value) == vec["o_weight"], f"i_vec={vec['i_vec']:03X}"
