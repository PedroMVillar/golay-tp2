# Construccion del informe. Requiere pdflatex (MiKTeX o TeX Live).
#
#   make            los PDF de todas las partes
#   make parte_a.pdf
#   make tablas     regenera gen/*.tex corriendo el modelo (la Parte B tarda ~1 min)
#   make clean      borra los auxiliares de LaTeX

PDFLATEX ?= pdflatex
PYTHON   ?= python

PARTES := parte_a parte_b
PDFS   := $(addsuffix .pdf,$(PARTES))
TABLAS := $(wildcard gen/*.tex)

.PHONY: all tablas clean
all: $(PDFS)

# Dos pasadas: la primera resuelve las referencias, la segunda las fija.
%.pdf: %.tex preambulo.tex $(TABLAS)
	$(PDFLATEX) -interaction=nonstopmode $< > /dev/null
	$(PDFLATEX) -interaction=nonstopmode $< > /dev/null
	@echo "$@ listo"

# Las tablas no se regeneran solas: dependen del modelo, no del .tex, y el
# barrido de la Parte B tarda. Se corre a mano cuando cambia golay/.
tablas:
	$(PYTHON) gen_parte_a.py
	$(PYTHON) gen_parte_b.py

clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk
