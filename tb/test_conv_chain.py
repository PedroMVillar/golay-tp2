# Pongo el interleaver y el deinterleaver uno detrás del otro. El primero
# desordena los bits y el segundo los vuelve a ordenar, así que lo que sale
# al final tiene que ser exactamente lo que entró, solo que atrasado. Meto
# bits al azar y me fijo que salgan iguales y con el retardo que da la cuenta.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge


@cocotb.test()
async def test_chain(dut):
    lam, j = int(dut.LAMBDA.value), int(dut.J.value)
    retardo = lam * (lam - 1) * j + 2
    cocotb.start_soon(Clock(dut.i_clk, 10, "ns").start())

    dut.i_rst.value = 1
    dut.i_bit.value = 0
    await FallingEdge(dut.i_clk)
    await FallingEdge(dut.i_clk)
    dut.i_rst.value = 0

    bits = [random.randint(0, 1) for _ in range(retardo * 3)]
    salida = []
    for b in bits:
        dut.i_bit.value = b
        await FallingEdge(dut.i_clk)
        salida.append(int(dut.o_bit.value))

    # el bit que metí en la vuelta t lo leo en la vuelta t + retardo - 1
    # (el -1 es porque en cada vuelta ya leo después del flanco)
    for t in range(len(bits) - retardo + 1):
        assert salida[t + retardo - 1] == bits[t], f"bit {t}"

    dut._log.info("LAMBDA=%d J=%d, retardo %d bits", lam, j, retardo)
