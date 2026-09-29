"""
Corre el modelo e imprime los resultados de la Parte B (Ejercicios 5 a 7).
Tarda medio minuto. Se corre desde la raíz del repo:

    python scripts/caracterizacion.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golay import (decode, decode_by_table, minimum_distance,
                   structure_summary, weight_distribution)
from golay import stimulus
from golay.sindromes import error_patterns

print("Ej 5 - distribucion de pesos:", dict(sorted(weight_distribution().items())))
print("       d_min =", minimum_distance())

print("\nEj 6 - tabla de sindromes:")
for (peso, n), cant in sorted(structure_summary().items()):
    print(f"       {cant} sindromes con {n} patron(es) de peso minimo {peso}")

print("\nEj 7a - errores de peso 0 a 4 sobre la palabra nula:")
for w in range(5):
    total = bien = otra = detectado = 0
    for e in error_patterns(w):
        total += 1
        res = decode(e)
        if res.uncorrectable:
            detectado += 1
        elif res.err == e:
            bien += 1
        else:
            otra += 1
        # de paso, el decodificador por tabla tiene que dar lo mismo
        tabla = decode_by_table(e)
        assert tabla.uncorrectable == res.uncorrectable
        assert res.uncorrectable or tabla.err == res.err
    print(f"       peso {w}: {total} patrones, {bien} corregidos, "
          f"{otra} a otra palabra, {detectado} detectados")

print("\nEj 7b - vectores para la Parte C:")
conteos = {
    "golay_mult_b": stimulus.mult_b_vectors(),
    "popcount12": stimulus.popcount12_vectors(),
    "golay_row_search": stimulus.row_search_vectors(),
    "golay_syndrome": stimulus.syndrome_vectors(),
    "golay_encoder": stimulus.encoder_vectors(),
}
for modulo, gen in conteos.items():
    print(f"       {modulo}: {sum(1 for _ in gen)}")
dec = list(stimulus.decoder_vectors())
print(f"       golay_decoder: {len(dec)}")
print("       por caso:", dict(sorted(stimulus.branch_coverage(dec).items())))
