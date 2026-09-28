# make         compila los pdf
# make tablas  regenera gen/ corriendo el modelo

PDFLATEX ?= pdflatex
PYTHON   ?= python

PDFS := parte_a.pdf parte_b.pdf

.PHONY: all tablas clean
all: $(PDFS)

%.pdf: %.tex preambulo.tex $(wildcard gen/*.tex)
	$(PDFLATEX) -interaction=nonstopmode $< > /dev/null
	$(PDFLATEX) -interaction=nonstopmode $< > /dev/null

tablas:
	$(PYTHON) gen_parte_a.py
	$(PYTHON) gen_parte_b.py

clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk
