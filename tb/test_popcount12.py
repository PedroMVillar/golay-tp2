# popcount12 cuenta cuántos unos tiene un vector. Pruebo los 4096 vectores
# posibles uno por uno y comparo lo que da el módulo con lo que da el modelo.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import popcount12_vectors


@cocotb.test()
async def test_popcount12(dut):
    for vec in popcount12_vectors():
        dut.i_vec.value = vec["i_vec"]
        # el módulo no tiene reloj, así que espero un toque a que calcule la salida
        await Timer(1, "ns")
        assert int(dut.o_weight.value) == vec["o_weight"], f"i_vec={vec['i_vec']:03X}"
