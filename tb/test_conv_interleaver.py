# Testbench del interleaver: bits al azar, uno por ciclo, comparados contra
# un modelo en Python con una lista por rama.

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge


def interleaver(bits, lam, j):
    ramas = [[0] * (i * j) for i in range(lam)]
    salida = []
    for t, b in enumerate(bits):
        rama = ramas[t % lam]
        if rama:
            rama.append(b)
            salida.append(rama.pop(0))
        else:
            salida.append(b)
    return salida


@cocotb.test()
async def test_interleaver(dut):
    lam, j = int(dut.LAMBDA.value), int(dut.J.value)
    cocotb.start_soon(Clock(dut.i_clk, 10, "ns").start())

    dut.i_rst.value = 1
    dut.i_bit.value = 0
    await FallingEdge(dut.i_clk)
    await FallingEdge(dut.i_clk)
    dut.i_rst.value = 0

    bits = [random.randint(0, 1) for _ in range(lam * lam * j * 4)]
    esperado = interleaver(bits, lam, j)

    for t, b in enumerate(bits):
        dut.i_bit.value = b
        await FallingEdge(dut.i_clk)
        assert int(dut.o_bit.value) == esperado[t], f"bit {t}"

    dut._log.info("LAMBDA=%d J=%d, %d bits", lam, j, len(bits))
