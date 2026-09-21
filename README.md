<div align="center">

# Código de Golay extendido (24,12)

**Fundación Fulgor** · Curso de FEC 2026 · TP2

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![SystemVerilog](https://img.shields.io/badge/SystemVerilog-RTL-9A4993?logo=verilog&logoColor=white)
![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-informe-008080?logo=latex&logoColor=white)
![Estado](https://img.shields.io/badge/Partes%20A%20y%20B-completas-2ea44f)
![Estado](https://img.shields.io/badge/Partes%20C%20y%20D-en%20curso-blue)

Trabajo Práctico 2 de FEC: propiedades del código de Golay extendido (24,12),
modelo de referencia en Python y decodificador implementado en RTL.

</div>

---

## Autor

- Villar, Pedro

---

## Mapa del repositorio

```
golay-tp2/
├── informe/           informe en LaTeX y los scripts que generan sus tablas
├── fec_algebra/       librería de GF(2^m) del TP1, base de la Parte B
├── golay/             modelo de referencia: matrices, codificador, decodificador
├── tests/             tests del modelo de referencia (pytest)
├── rtl/               submódulos RTL (Parte C), un archivo por módulo
├── rtl_bonus/         interleaver/deinterleaver convolucional (Parte D)
├── tb/                testbenches de cocotb, uno por submódulo + integración
└── sim/               Makefiles de simulación
```

No hay carpeta de vectores de prueba: siguiendo el patrón de la cátedra en la
Unidad 3, los testbenches importan el modelo de Python por `PYTHONPATH` y
generan el estímulo adentro del propio test. Ver
[`golay/stimulus.py`](golay/stimulus.py).

---

## Dónde está resuelto cada ejercicio

### Parte A — Propiedades del código · `completa`

Informe: [`informe/parte_a.pdf`](informe/parte_a.pdf)

| Ej. | Tema | Dónde |
|:--:|---|---|
| 1 | Matrices, parámetros, codificación a mano | [`informe/parte_a.tex`](informe/parte_a.tex) §1 |
| 2 | Distancia mínima y capacidad de corrección | [`informe/parte_a.tex`](informe/parte_a.tex) §2 |
| 3 | Decodificación manual de `r1`, `r2`, `r3` | [`informe/parte_a.tex`](informe/parte_a.tex) §3 |

Las cuentas están desarrolladas paso a paso, no resumidas en el resultado: el
XOR acumulado fila por fila, los doce candidatos `s ⊕ bᵢ` de cada búsqueda con
su peso, y las 78 entradas de `B²` que hacen falta aprovechando la simetría.
Las tablas largas las genera
[`informe/gen_parte_a.py`](informe/gen_parte_a.py) hacia `informe/gen/`, para
no copiar unos 300 números a mano al `.tex`.

### Parte B — Modelo de referencia · `completa`

Informe: [`informe/parte_b.pdf`](informe/parte_b.pdf)

| Ej. | Tema | Dónde |
|:--:|---|---|
| 4 | `GF(2^m)` con m = 1, y álgebra matricial nueva | [`golay/bits.py`](golay/bits.py), [`golay/linalg.py`](golay/linalg.py) |
| 5 | Construcción de G y H; enumeración y pesos | [`golay/matrices.py`](golay/matrices.py), [`golay/encoder.py`](golay/encoder.py) |
| 6 | Codificador, decodificador de cuatro casos | [`golay/encoder.py`](golay/encoder.py), [`golay/decoder.py`](golay/decoder.py) |
| 6 | Tabla de síndromes generada a partir de H | [`golay/cosets.py`](golay/cosets.py) |
| 7a | Caracterización del decodificador | [`informe/gen_parte_b.py`](informe/gen_parte_b.py) |
| 7b | Estímulo para los testbenches de la Parte C | [`golay/stimulus.py`](golay/stimulus.py) |

La redacción va en [`informe/parte_b.tex`](informe/parte_b.tex), que además
responde las dos preguntas que pide el enunciado: por qué el síndrome no
depende del mensaje transmitido, y por qué `d_min = 8` detecta cuatro errores
pero no los corrige.

### Partes C y D — RTL

| Ej. | Tema | Dónde |
|:--:|---|---|
| 8 | Codificador (`golay_mult_b`, `popcount12`, `golay_encoder`) | pendiente |
| 9 | Decodificador pipelineado de tres etapas | pendiente |
| 10 | Verificación y análisis | pendiente |
| 11 | Interleaver convolucional (bonus) | pendiente |

---

## Cómo correr el modelo

```bash
pip install pytest
pytest                  # suite del modelo de referencia

cd informe
make                    # compila los PDF de todas las partes
make tablas             # regenera gen/*.tex corriendo el modelo (~1 min)
make clean              # borra los auxiliares de LaTeX
```

Los scripts de `informe/` verifican sus propios resultados contra las tablas
del enunciado con `assert`: si algún número no coincide, fallan en vez de
escribir un `.tex` equivocado. Las partes comparten
[`informe/preambulo.tex`](informe/preambulo.tex).

### Para la Parte C

```bash
pip install cocotb
```

más un simulador. El de la cátedra es Icarus Verilog (`SIM=icarus`); en
Windows conviene el instalador de [bleyer.org](https://bleyer.org/icarus/),
que no pide privilegios de administrador.

Los Makefiles de simulación tienen que armar el `PYTHONPATH` con el separador
del sistema, no con `:` fijo. En Windows las rutas ya llevan `C:`, así que un
`:` no se interpreta como separador y el testbench no encuentra el modelo
—falla en silencio, con un `ModuleNotFoundError` que no dice por qué:

```makefile
ifeq ($(OS),Windows_NT)
    PATHSEP := ;
else
    PATHSEP := :
endif
export PYTHONPATH := $(REPO)$(PATHSEP)$(PYTHONPATH)
```

---

## Enunciado

[TP2_FEC.pdf](TP2_FEC.pdf)

---

## Librería base

La Parte B se apoya en [`fec_algebra`](fec_algebra/), la librería de campos de
Galois desarrollada en el TP1 de este mismo curso ([repo original](https://github.com/PedroMVillar/FEC-Fulgor)).
Se instancia en `GF(2^1)` con `P(x) = x + 1`, o sea GF(2), y no hizo falta
modificarla: ninguna parte de la implementación asumía `m ≥ 2`. Sobre esa base
se agregó el álgebra matricial que el trabajo anterior no cubría
([`golay/linalg.py`](golay/linalg.py)): producto vector-matriz, matriz-matriz y
peso de Hamming.

---

## Una discrepancia con el enunciado

El Ejercicio 9 escribe el síndrome como `s = r[23:12] ⊕ B·r[11:0]`, pero esa
expresión intercambia los dos bloques y es inconsistente con la tabla de cuatro
casos: con ella el caso 1 pediría `e₂ = s·B` en lugar de `e₂ = s`, y los
conteos del Ejercicio 7a no dan. El modelo usa `s = H·rᵀ = B·r[23:12] ⊕ r[11:0]`,
que es la que sale del `H = [B | I₁₂]` definido en la portada del propio
enunciado y la única que reproduce esos conteos. Está documentado en
[`golay/decoder.py`](golay/decoder.py) y en el informe.
