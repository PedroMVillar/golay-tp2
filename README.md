<div align="center">

# Código de Golay extendido (24,12)

**Fundación Fulgor** · Curso de FEC 2026 · TP2

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![SystemVerilog](https://img.shields.io/badge/SystemVerilog-RTL-9A4993?logo=verilog&logoColor=white)
![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-informe-008080?logo=latex&logoColor=white)
![Estado](https://img.shields.io/badge/estado-en%20curso-blue)

Trabajo Práctico 2 de FEC: propiedades del código de Golay extendido (24,12),
modelo de referencia en Python y decodificador implementado en RTL.

</div>

---

## Integrantes

- Svane, Nicolas
- Villar, Pedro 

---

## Mapa del repositorio

```
golay-tp2/
├── informe/           informe en LaTeX (Partes A, B, C, D) y PDF final
├── fec_algebra/       librería de GF(2^m) del TP1, base de la Parte B
├── golay/             modelo de referencia: matrices, codificador, decodificador
├── tests/             tests del modelo de referencia (pytest)
├── vectors/           vectores de prueba, fuente única para Python y RTL
├── rtl/               submódulos RTL (Parte C), un archivo por módulo
├── rtl_bonus/         interleaver/deinterleaver convolucional (Parte D)
├── tb/                testbenches, uno por submódulo + integración
└── sim/               scripts de simulación
```

---

## Enunciado

[TP2_FEC.pdf](TP2_FEC.pdf)

---

## Librería base

La Parte B se apoya en [`fec_algebra`](fec_algebra/), la librería de campos de
Galois desarrollada en el TP1 de este mismo curso ([repo original](https://github.com/PedroMVillar/FEC-Fulgor)).
Sobre esa base se agregó el álgebra matricial (`golay/linalg.py`) necesaria
para este trabajo: producto vector-matriz, matriz-matriz y peso de Hamming.
