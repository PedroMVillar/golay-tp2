# Testbench de golay_err_gen, con las entradas que le llegarían desde el
# pipeline para cada palabra del conjunto del decodificador.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import err_gen_vectors

ENTRADAS = ["i_syn", "i_q", "i_res_syn", "i_res_q", "i_w_syn", "i_w_q",
            "i_idx_syn", "i_idx_q", "i_found_syn", "i_found_q"]


@cocotb.test()
async def test_err_gen(dut):
    for vec in err_gen_vectors():
        for nombre in ENTRADAS:
            getattr(dut, nombre).value = vec[nombre]
        await Timer(1, "ns")
        msg = f"caso {vec['_case']}, s={vec['i_syn']:03X}"
        assert int(dut.o_uncorrectable.value) == vec["o_uncorrectable"], msg
        if not vec["o_uncorrectable"]:
            assert int(dut.o_err.value) == vec["o_err"], msg
