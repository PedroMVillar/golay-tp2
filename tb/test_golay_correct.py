# Testbench de golay_correct.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import correct_vectors


@cocotb.test()
async def test_correct(dut):
    for vec in correct_vectors():
        dut.i_rx.value = vec["i_rx"]
        dut.i_err.value = vec["i_err"]
        await Timer(1, "ns")
        msg = f"i_rx={vec['i_rx']:06X} i_err={vec['i_err']:06X}"
        assert int(dut.o_cw.value) == vec["o_cw"], msg
        assert int(dut.o_msg.value) == vec["o_msg"], msg
        assert int(dut.o_corrected.value) == vec["o_corrected"], msg
