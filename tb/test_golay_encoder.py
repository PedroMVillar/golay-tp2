# Meto los 4096 mensajes, uno por ciclo de reloj. Como el codificador
# tiene un registro a la salida, la palabra aparece en el ciclo siguiente,
# así que después de cada flanco me fijo que la salida sea la palabra del
# mensaje que acabo de meter.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge

from golay.stimulus import encoder_vectors


@cocotb.test()
async def test_encoder(dut):
    cocotb.start_soon(Clock(dut.i_clk, 10, "ns").start())

    dut.i_rst.value = 1
    dut.i_msg.value = 0
    await FallingEdge(dut.i_clk)
    await FallingEdge(dut.i_clk)
    dut.i_rst.value = 0

    for vec in encoder_vectors():
        dut.i_msg.value = vec["i_msg"]
        await FallingEdge(dut.i_clk)
        assert int(dut.o_cw.value) == vec["o_cw"], f"i_msg={vec['i_msg']:03X}"
