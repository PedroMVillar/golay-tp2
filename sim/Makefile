# make TOP=golay_decoder   corre el testbench de un módulo
# make todos               corre todos
# make TOP=conv_chain LAMBDA=5 J=3   el interleaver con otros parámetros

SIM ?= icarus
TOPLEVEL_LANG = verilog
TOP ?= golay_decoder

VERILOG_SOURCES = $(wildcard ../rtl/*.sv) $(wildcard ../rtl-bonus/*.sv) ../tb/conv_chain.sv
COCOTB_TOPLEVEL = $(TOP)
COCOTB_TEST_MODULES = test_$(TOP)
SIM_BUILD = sim_build/$(TOP)

ifdef LAMBDA
    COMPILE_ARGS += -P$(TOP).LAMBDA=$(LAMBDA)
    SIM_BUILD := $(SIM_BUILD)_$(LAMBDA)_$(J)
endif
ifdef J
    COMPILE_ARGS += -P$(TOP).J=$(J)
endif

# en Windows el separador del PYTHONPATH es ;
ifeq ($(OS),Windows_NT)
    SEP := ;
else
    SEP := :
endif
export PYTHONPATH := ../tb$(SEP)..

MODULOS = golay_mult_b popcount12 golay_row_search golay_syndrome \
          golay_err_gen golay_correct golay_encoder golay_decoder \
          conv_chain

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: todos
todos:
	for m in $(MODULOS); do $(MAKE) TOP=$$m || exit 1; done
