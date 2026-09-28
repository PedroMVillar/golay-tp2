"""
Corre el modelo de golay/ y genera las tablas de la Parte B en gen/.
Chequea los resultados contra las tablas del enunciado. Tarda medio minuto.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golay import (all_codewords, decode, decode_by_table, minimum_distance,
                   structure_summary, weight_distribution)
from golay import stimulus
from golay.cosets import error_patterns

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen")
os.makedirs(OUT, exist_ok=True)

EJ7A_ESPERADO = {
    0: (1, 1, 0),
    1: (24, 24, 0),
    2: (276, 276, 0),
    3: (2024, 2024, 0),
    4: (10626, 0, 10626),
}
PESOS_ESPERADO = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}


def write(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write("% generado por gen_parte_b.py -- no editar a mano\n")
        f.write(body + "\n")
    print("  ->", "gen/" + name)


# Ejercicio 5: distribución de pesos
pesos = weight_distribution()
assert dict(pesos) == PESOS_ESPERADO
assert minimum_distance() == 8

cols = sorted(pesos)
write("tabla_pesos_modelo.tex", "\n".join([
    r"\begin{tabular}{@{}l*{5}{c}r@{}}", r"\toprule",
    r"peso $w$ & " + " & ".join(map(str, cols)) + r" & total \\",
    r"\midrule",
    r"modelo & " + " & ".join(str(pesos[w]) for w in cols) + r" & 4096 \\",
    r"enunciado & " + " & ".join(str(PESOS_ESPERADO[w]) for w in cols) + r" & 4096 \\",
    r"\bottomrule", r"\end{tabular}",
]))

# Ejercicio 7a: todos los errores de peso <= 4 sobre la palabra nula
resultado = {}
for w in range(5):
    total = exacto = otra = detectado = 0
    for e in error_patterns(w):
        total += 1
        res = decode(e)
        if res.uncorrectable:
            detectado += 1
        elif res.err == e:
            exacto += 1
        else:
            otra += 1
    resultado[w] = (total, exacto, otra, detectado)
    print("peso", w, resultado[w])
    assert (total, exacto, detectado) == EJ7A_ESPERADO[w]
    assert otra == 0

L = [r"\begin{tabular}{@{}l*{5}{r}@{}}", r"\toprule",
     r"peso de $e$ & 0 & 1 & 2 & 3 & 4 \\", r"\midrule"]
for etiqueta, k in (("patrones", 0), ("corregidos bien", 1),
                    ("decodificados a otra palabra", 2),
                    ("detectados como no corregibles", 3)):
    L.append(etiqueta + " & " + " & ".join(str(resultado[w][k]) for w in range(5)) + r" \\")
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_ej7a.tex", "\n".join(L))

# Ejercicio 6: tabla de síndromes
estructura = structure_summary()
assert sum(estructura.values()) == 4096
corregibles = sum(c for (w, n), c in estructura.items() if n == 1)
assert corregibles == 1 + 24 + 276 + 2024

L = [r"\begin{tabular}{@{}cccl@{}}", r"\toprule",
     r"peso del líder & líderes & cosets & \\", r"\midrule"]
for (peso, n), cant in sorted(estructura.items()):
    nota = "corregible" if n == 1 else "no corregible"
    L.append(r"%d & %d & %d & %s \\" % (peso, n, cant, nota))
L += [r"\midrule", r"& & 4096 & \\", r"\bottomrule", r"\end{tabular}"]
write("tabla_cosets.tex", "\n".join(L))

# comparo los dos decodificadores sobre una muestra
for cw in all_codewords()[::37]:
    for e in [1 << i for i in range(6)] + [0b111 << i for i in range(6)] + [0xF << i for i in range(6)]:
        a, b = decode(cw ^ e), decode_by_table(cw ^ e)
        assert a.uncorrectable == b.uncorrectable
        assert a.uncorrectable or (a.msg, a.err) == (b.msg, b.err)

# Ejercicio 7b: cuánto estímulo hay para cada módulo
conteos = [
    ("golay\\_mult\\_b", sum(1 for _ in stimulus.mult_b_vectors()), "exhaustivo"),
    ("popcount12", sum(1 for _ in stimulus.popcount12_vectors()), "exhaustivo"),
    ("golay\\_row\\_search", sum(1 for _ in stimulus.row_search_vectors()), "exhaustivo"),
    ("golay\\_encoder", sum(1 for _ in stimulus.encoder_vectors()), "exhaustivo"),
    ("golay\\_syndrome", sum(1 for _ in stimulus.syndrome_vectors()),
     "palabras código $+$ errores"),
]
vec_dec = list(stimulus.decoder_vectors())
cobertura = stimulus.branch_coverage(vec_dec)
assert set(cobertura) == {1, 2, 3, 4, 5}
conteos.append(("golay\\_decoder", len(vec_dec), "muestra, cubre los 5 casos"))

L = [r"\begin{tabular}{@{}lrl@{}}", r"\toprule",
     r"módulo & casos & \\", r"\midrule"]
for mod, n, criterio in conteos:
    L.append(r"\texttt{%s} & %d & %s \\" % (mod, n, criterio))
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_estimulo.tex", "\n".join(L))

condicion = {1: r"$w(s)\le 3$", 2: r"$\exists i: w(s\oplus b_i)\le 2$",
             3: r"$w(q)\le 3$", 4: r"$\exists i: w(q\oplus b_i)\le 2$",
             5: "no corregible"}
L = [r"\begin{tabular}{@{}crl@{}}", r"\toprule",
     r"caso & vectores & condición \\", r"\midrule"]
for c in sorted(cobertura):
    L.append(r"%d & %d & %s \\" % (c, cobertura[c], condicion[c]))
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_cobertura.tex", "\n".join(L))

write("constantes_b.tex", "\n".join([
    r"\newcommand{\dmin}{%d}" % minimum_distance(),
    r"\newcommand{\nCosetsCorregibles}{%d}" % corregibles,
    r"\newcommand{\nCosetsAmbiguos}{%d}" % (4096 - corregibles),
]))
