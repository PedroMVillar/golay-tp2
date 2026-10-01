# err_gen recibe todo lo que calcularon las etapas anteriores y decide en
# qué caso cae la palabra y cuál es el error. Inventarle entradas al azar
# no tiene sentido, así que uso palabras recibidas de verdad: el modelo
# calcula lo que le llegaría al módulo y lo que debería salir.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import err_gen_vectors


@cocotb.test()
async def test_err_gen(dut):
    for vec in err_gen_vectors():
        dut.i_syn.value = vec["i_syn"]
        dut.i_q.value = vec["i_q"]
        dut.i_res_syn.value = vec["i_res_syn"]
        dut.i_res_q.value = vec["i_res_q"]
        dut.i_w_syn.value = vec["i_w_syn"]
        dut.i_w_q.value = vec["i_w_q"]
        dut.i_idx_syn.value = vec["i_idx_syn"]
        dut.i_idx_q.value = vec["i_idx_q"]
        dut.i_found_syn.value = vec["i_found_syn"]
        dut.i_found_q.value = vec["i_found_q"]
        # el módulo no tiene reloj, así que espero un toque a que calcule la salida
        await Timer(1, "ns")

        msg = f"caso {vec['_case']}, s={vec['i_syn']:03X}"
        assert int(dut.o_uncorrectable.value) == vec["o_uncorrectable"], msg
        if not vec["o_uncorrectable"]:
            assert int(dut.o_err.value) == vec["o_err"], msg
