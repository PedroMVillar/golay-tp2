# Testbench de interleaver + deinterleaver en cadena: lo que sale tiene
# que ser lo mismo que entró, atrasado LAMBDA*(LAMBDA-1)*J bits más los
# dos registros de salida.

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

    # el bit t entra en el flanco t y sale en el flanco t + retardo - 1
    assert salida[retardo - 1:] == bits[:len(bits) - retardo + 1]

    dut._log.info("LAMBDA=%d J=%d, retardo %d bits", lam, j, retardo)
