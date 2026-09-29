# Testbench del decodificador completo. Entra una palabra por ciclo y la
# salida de cada una se compara tres ciclos después contra el modelo:
# mensaje y patrón de error bit a bit, y las dos banderas.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge

from golay.stimulus import branch_coverage, decoder_vectors

LATENCIA = 3


def chequear(dut, vec):
    msg = f"i_rx={vec['i_rx']:06X} caso {vec['_case']}"
    assert int(dut.o_uncorrectable.value) == vec["o_uncorrectable"], msg
    assert int(dut.o_corrected.value) == vec["o_corrected"], msg
    if not vec["o_uncorrectable"]:
        assert int(dut.o_msg.value) == vec["o_msg"], msg
        assert int(dut.o_err.value) == vec["o_err"], msg


@cocotb.test()
async def test_decoder(dut):
    cocotb.start_soon(Clock(dut.i_clk, 10, "ns").start())

    dut.i_rst.value = 1
    dut.i_rx.value = 0
    await FallingEdge(dut.i_clk)
    await FallingEdge(dut.i_clk)
    dut.i_rst.value = 0

    vectores = list(decoder_vectors())
    pendientes = []
    for vec in vectores + [None] * (LATENCIA - 1):
        if vec is not None:
            dut.i_rx.value = vec["i_rx"]
        await FallingEdge(dut.i_clk)
        pendientes.append(vec)
        if len(pendientes) == LATENCIA:
            chequear(dut, pendientes.pop(0))

    dut._log.info("vectores: %d, por caso: %s", len(vectores),
                  dict(sorted(branch_coverage(vectores).items())))
