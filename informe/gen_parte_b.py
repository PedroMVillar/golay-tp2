# -*- coding: utf-8 -*-
"""
Caracterización del decodificador (Ejercicio 7a) y tablas de la Parte B.

Corre los barridos pesados sobre el modelo de :mod:`golay` y escribe los
resultados como fragmentos LaTeX en ``gen/``. Ningún número del informe se
copia a mano: salen todos de acá.

    python gen_parte_b.py     ->  gen/*.tex

Tarda alrededor de medio minuto: recorre los 12951 patrones de error de
peso <= 4, construye la tabla de 4096 síndromes y cuenta el estímulo que
se le va a pasar a la Parte C.
"""

import os
import sys
import time

from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golay import (CW_BITS, all_codewords, decode, decode_by_table,
                   minimum_distance, structure_summary, weight_distribution)
from golay import stimulus

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen")
os.makedirs(OUT, exist_ok=True)

#: La tabla que el enunciado da como resultado esperado del Ejercicio 7a.
EJ7A_ESPERADO = {
    0: (1, 1, 0),
    1: (24, 24, 0),
    2: (276, 276, 0),
    3: (2024, 2024, 0),
    4: (10626, 0, 10626),
}

#: Distribución de pesos del enunciado (Ejercicio 2).
PESOS_ESPERADO = {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}


def write(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("% generado por gen_parte_b.py -- no editar a mano\n")
        f.write(body)
        f.write("\n")
    print("  ->", os.path.join("gen", name))


def patrones(peso):
    """Todos los patrones de error de 24 bits de un peso dado."""
    for pos in combinations(range(CW_BITS), peso):
        e = 0
        for p in pos:
            e |= 1 << p
        yield e


# ============================================== Ej. 5: distribución de pesos
print("Ejercicio 5: distribución de pesos por fuerza bruta...")
t0 = time.time()
pesos = weight_distribution()
assert dict(pesos) == PESOS_ESPERADO, dict(pesos)
assert sum(pesos.values()) == 4096
assert minimum_distance() == 8
print("   %d palabras, d_min = %d  (%.1f s)" % (sum(pesos.values()),
                                                minimum_distance(),
                                                time.time() - t0))

L = [r"\begin{tabular}{@{}l*{5}{c}r@{}}", r"\toprule",
     r"peso $w$ & " + " & ".join(str(w) for w in sorted(pesos)) + r" & total \\",
     r"\midrule",
     r"modelo (fuerza bruta) & "
     + " & ".join(str(pesos[w]) for w in sorted(pesos))
     + r" & %d \\" % sum(pesos.values()),
     r"enunciado & "
     + " & ".join(str(PESOS_ESPERADO[w]) for w in sorted(PESOS_ESPERADO))
     + r" & %d \\" % sum(PESOS_ESPERADO.values()),
     r"\bottomrule", r"\end{tabular}"]
write("tabla_pesos_modelo.tex", "\n".join(L))


# =============================== Ej. 7a: caracterización del decodificador
print("Ejercicio 7a: barrido de los patrones de error de peso <= 4...")
t0 = time.time()
resultado = {}
for w in range(5):
    total = exacto = otra = detectado = 0
    for e in patrones(w):
        total += 1
        # El código es lineal y el síndrome solo depende de e, así que
        # decodificar e es equivalente a decodificar cualquier v + e.
        res = decode(e)
        if res.uncorrectable:
            detectado += 1
        elif res.err == e:
            exacto += 1
        else:
            otra += 1
    resultado[w] = (total, exacto, otra, detectado)
    print("   peso %d: %5d patrones, %5d exactos, %5d a otra palabra, %5d detectados"
          % (w, total, exacto, otra, detectado))
print("   (%.1f s)" % (time.time() - t0))

for w, (total, exacto, otra, detectado) in resultado.items():
    esp_total, esp_corr, esp_det = EJ7A_ESPERADO[w]
    assert (total, exacto, detectado) == (esp_total, esp_corr, esp_det), (w, resultado[w])
    assert otra == 0, "el enunciado no admite decodificación a otra palabra"

L = [r"\begin{tabular}{@{}l*{5}{r}@{}}", r"\toprule",
     r"peso de $e$ & " + " & ".join(str(w) for w in sorted(resultado)) + r" \\",
     r"\midrule"]
for etiqueta, idx in ((r"patrones", 0), (r"corregidos de forma exacta", 1),
                      (r"decodificados a otra palabra", 2),
                      (r"detectados como no corregibles", 3)):
    L.append(etiqueta + " & "
             + " & ".join(str(resultado[w][idx]) for w in sorted(resultado))
             + r" \\")
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_ej7a.tex", "\n".join(L))


# ============================ Ej. 6: estructura de cosets (tabla de síndromes)
print("Ejercicio 6: estructura de la tabla de síndromes...")
t0 = time.time()
estructura = structure_summary()
print("   %d cosets  (%.1f s)" % (sum(estructura.values()), time.time() - t0))

L = [r"\begin{tabular}{@{}cccl@{}}", r"\toprule",
     r"peso del líder & líderes mínimos & cosets & \\", r"\midrule"]
for (peso, n_lideres), cant in sorted(estructura.items()):
    nota = "corregible" if n_lideres == 1 else "ambiguo, solo detectable"
    L.append(r"%d & %d & %d & %s \\" % (peso, n_lideres, cant, nota))
L += [r"\midrule",
      r"& & %d & $= 2^{12}$ \\" % sum(estructura.values()),
      r"\bottomrule", r"\end{tabular}"]
write("tabla_cosets.tex", "\n".join(L))

assert sum(estructura.values()) == 4096
corregibles = sum(c for (w, n), c in estructura.items() if n == 1)
assert corregibles == 1 + 24 + 276 + 2024

# Por qué son exactamente seis: dos líderes de peso 4 del mismo coset
# difieren en una palabra código, que no puede pesar menos de 8; como
# w(e) + w(e') = 8, los soportes tienen que ser disjuntos. Seis bloques
# disjuntos de cuatro posiciones cubren las 24: es un sexteto.
print("Estructura de sexteto de los cosets ambiguos...")
from golay import coset_table
ambiguos = [c for c in coset_table().values() if c.weight == 4]
for c in ambiguos:
    ls = c.leaders
    assert all((ls[i] & ls[j]) == 0 for i in range(6) for j in range(i + 1, 6))
    union = 0
    for e in ls:
        union |= e
    assert union == (1 << CW_BITS) - 1
print("   los %d cosets de peso 4 son sextetos (6 bloques disjuntos de 4)"
      % len(ambiguos))

ejemplo = min(ambiguos, key=lambda c: c.syndrome)
L = [r"\begin{tabular}{@{}rl@{}}", r"\toprule",
     r"líder & soporte \\", r"\midrule"]
for k, e in enumerate(sorted(ejemplo.leaders, reverse=True)):
    bits = format(e, "024b")
    L.append(r"$e_{%d}$ & \texttt{%s} \\"
             % (k + 1, r"\,".join(bits[i:i + 4] for i in range(0, 24, 4))))
L += [r"\midrule",
      r"$\bigvee$ & \texttt{%s} \\"
      % r"\,".join(["1111"] * 6),
      r"\bottomrule", r"\end{tabular}"]
write("tabla_sexteto.tex", "\n".join(L))


# ================================= cruce entre los dos decodificadores
print("Cruce: cuatro casos contra tabla de síndromes...")
t0 = time.time()
discrepancias = 0
muestra = list(all_codewords()[::37])
for cw in muestra:
    for e in list(patrones(1))[:6] + list(patrones(3))[:6] + list(patrones(4))[:6]:
        a, b = decode(cw ^ e), decode_by_table(cw ^ e)
        if a.uncorrectable != b.uncorrectable:
            discrepancias += 1
        elif not a.uncorrectable and (a.msg, a.err) != (b.msg, b.err):
            discrepancias += 1
n_cruce = len(muestra) * 18
print("   %d casos, %d discrepancias  (%.1f s)" % (n_cruce, discrepancias,
                                                   time.time() - t0))
assert discrepancias == 0


# ================================ Ej. 7b: estímulo para la Parte C
print("Ejercicio 7b: contando el estímulo de la Parte C...")
t0 = time.time()
conteos = [
    ("golay\\_mult\\_b", "mult\\_b\\_vectors", sum(1 for _ in stimulus.mult_b_vectors()),
     "barrido exhaustivo"),
    ("popcount12", "popcount12\\_vectors", sum(1 for _ in stimulus.popcount12_vectors()),
     "barrido exhaustivo"),
    ("golay\\_row\\_search", "row\\_search\\_vectors",
     sum(1 for _ in stimulus.row_search_vectors()), "barrido exhaustivo"),
    ("golay\\_encoder", "encoder\\_vectors", sum(1 for _ in stimulus.encoder_vectors()),
     "barrido exhaustivo"),
    ("golay\\_syndrome", "syndrome\\_vectors", sum(1 for _ in stimulus.syndrome_vectors()),
     "4096 palabras código $+$ errores"),
]
vectores_dec = list(stimulus.decoder_vectors())
cobertura = stimulus.branch_coverage(vectores_dec)
conteos.append(("golay\\_decoder", "decoder\\_vectors", len(vectores_dec),
                "curado, cinco ramas"))
print("   %.1f s" % (time.time() - t0))
for mod, _, n, _ in conteos:
    print("   %-22s %6d" % (mod.replace("\\", ""), n))
print("   cobertura de ramas:", dict(sorted(cobertura.items())))

assert set(cobertura) == {1, 2, 3, 4, 5}, dict(cobertura)

L = [r"\begin{tabular}{@{}lllr@{}}", r"\toprule",
     r"módulo & generador & casos & criterio \\", r"\midrule"]
for mod, gen, n, criterio in conteos:
    L.append(r"\texttt{%s} & \texttt{%s} & %d & %s \\" % (mod, gen, n, criterio))
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_estimulo.tex", "\n".join(L))

L = [r"\begin{tabular}{@{}cr l@{}}", r"\toprule",
     r"rama & casos & resuelve por \\", r"\midrule"]
ramas = {1: r"$w(s)\le 3$", 2: r"$\exists i: w(s\oplus b_i)\le 2$",
         3: r"$w(q)\le 3$", 4: r"$\exists i: w(q\oplus b_i)\le 2$",
         5: r"no corregible"}
for rama in sorted(cobertura):
    L.append(r"%d & %d & %s \\" % (rama, cobertura[rama], ramas[rama]))
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_cobertura.tex", "\n".join(L))

write("constantes_b.tex", "\n".join([
    r"\newcommand{\dmin}{%d}" % minimum_distance(),
    r"\newcommand{\nCosetsCorregibles}{%d}" % corregibles,
    r"\newcommand{\nCosetsAmbiguos}{%d}" % (4096 - corregibles),
    r"\newcommand{\nVectoresDecoder}{%d}" % len(vectores_dec),
]))

print("\nTodo verificado contra las tablas del enunciado.")
