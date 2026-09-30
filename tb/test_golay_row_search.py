# Para cada uno de los 4096 vectores, el módulo busca la primera fila de B
# que, sumada al vector, lo deje con 2 unos o menos. Comparo si la
# encontró, qué fila eligio y cómo quedó el vector. Si no encontro
# ninguna, solo miro o_found, porque lo demás no es nada

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import row_search_vectors


@cocotb.test()
async def test_row_search(dut):
    for vec in row_search_vectors():
        dut.i_vec.value = vec["i_vec"]
        await Timer(1, "ns")
        msg = f"i_vec={vec['i_vec']:03X}"
        assert int(dut.o_found.value) == vec["o_found"], msg
        if vec["o_found"]:
            assert int(dut.o_idx.value) == vec["o_idx"], msg
            assert int(dut.o_res.value) == vec["o_res"], msg
