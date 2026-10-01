# Le paso al módulo los 4096 vectores posibles de 12 bits y me fijo que la
# salida sea la misma que calcula el modelo en Python. Además, cada salida
# la vuelvo a meter como entrada: como B·B = I, multiplicar dos veces por
# B tiene que devolver el vector original.

import cocotb
from cocotb.triggers import Timer

from golay.stimulus import mult_b_vectors


@cocotb.test()
async def test_mult_b(dut):
    for vec in mult_b_vectors():
        dut.i_vec.value = vec["i_vec"]
        # el módulo no tiene reloj, así que espero un toque a que calcule la salida
        await Timer(1, "ns")
        salida = int(dut.o_vec.value)
        assert salida == vec["o_vec"], f"i_vec={vec['i_vec']:03X}"

        dut.i_vec.value = salida
        await Timer(1, "ns")
        assert int(dut.o_vec.value) == vec["i_vec"], f"B^2 != I en {vec['i_vec']:03X}"
