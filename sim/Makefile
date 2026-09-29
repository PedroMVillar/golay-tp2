# make TOP=golay_decoder   corre el testbench de un módulo
# make todos               corre todos

SIM ?= icarus
TOPLEVEL_LANG = verilog
TOP ?= golay_decoder

VERILOG_SOURCES = $(wildcard ../rtl/*.sv)
COCOTB_TOPLEVEL = $(TOP)
COCOTB_TEST_MODULES = test_$(TOP)
SIM_BUILD = sim_build/$(TOP)

# en Windows el separador del PYTHONPATH es ;
ifeq ($(OS),Windows_NT)
    SEP := ;
else
    SEP := :
endif
export PYTHONPATH := ../tb$(SEP)..

MODULOS = golay_mult_b popcount12 golay_row_search golay_syndrome \
          golay_err_gen golay_correct golay_encoder golay_decoder

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: todos
todos:
	for m in $(MODULOS); do $(MAKE) TOP=$$m || exit 1; done
