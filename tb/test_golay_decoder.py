# Le mando al decodificador una palabra por ciclo, sin esperar a que salga
# la anterior, como funcionaría de verdad. Cada palabra tarda 3 ciclos en
# salir, así que voy guardando lo que mandé y comparo cada salida con la
# palabra de hace 3 ciclos: mensaje, error y las dos banderas. Hay palabras
# sin error, con 1 a 3 errores (se tienen que corregir) y con 4 errores
# (se tienen que marcar como no corregibles).

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
    for vec in vectores:
        dut.i_rx.value = vec["i_rx"]
        await FallingEdge(dut.i_clk)
        pendientes.append(vec)
        # lo que sale ahora es la palabra que mandé hace 3 ciclos
        if len(pendientes) == LATENCIA:
            chequear(dut, pendientes.pop(0))

    # las dos últimas siguen adentro del pipeline, espero a que salgan
    while pendientes:
        await FallingEdge(dut.i_clk)
        chequear(dut, pendientes.pop(0))

    dut._log.info("vectores: %d, por caso: %s", len(vectores),
                  dict(sorted(branch_coverage(vectores).items())))
