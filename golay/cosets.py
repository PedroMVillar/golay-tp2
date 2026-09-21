"""
Tabla de síndromes derivada de H, y el decodificador por tabla.

El Ejercicio 6 pide que la tabla de síndromes se genere de forma
programática a partir de H. El algoritmo de cuatro casos no necesita
ninguna tabla (resuelve por pesos y búsqueda sobre las filas ``b_i``), así
que acá la tabla cumple otro rol: es un **decodificador independiente**
que sirve de oráculo para verificar al de cuatro casos, sin compartir una
sola línea de lógica con él.

Estructura del código
---------------------
Recorriendo todos los patrones de error de peso ≤ 4 y agrupándolos por
síndrome sale la estructura completa del código:

=========  =======  ==================
cosets     peso     líderes mínimos
=========  =======  ==================
1          0        1
24         1        1
276        2        1
2024       3        1
1771       4        6
=========  =======  ==================

Los 2325 cosets de peso ≤ 3 tienen líder **único**: por eso esos patrones
se corrigen. Los 1771 restantes tienen seis líderes de peso 4 empatados:
por eso son ambiguos y solo se pueden detectar. La tabla del Ejercicio 7a
no es un dato empírico, es esta estructura.

Notar que ``2325 + 1771 = 4096`` (todos los síndromes quedan cubiertos) y
que ``1771 × 6 = 10626`` (todos los patrones de peso 4).
"""

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations

from fec_algebra import GF

from .bits import GF2, CW_BITS, MSG_BITS, split_cw
from .decoder import DecodeResult, syndrome

#: Peso máximo que hace falta recorrer para cubrir los 4096 síndromes.
MAX_LEADER_WEIGHT = 4


@dataclass(frozen=True)
class Coset:
    """Un coset del código, identificado por su síndrome.

    Attributes:
        syndrome: el síndrome común a todo el coset, 12 bits.
        weight: peso de los líderes (el mínimo del coset).
        leaders: todos los patrones de error de ese peso mínimo.
    """

    syndrome: int
    weight: int
    leaders: tuple

    @property
    def unique(self) -> bool:
        """¿Hay un solo líder de peso mínimo? Si no, el coset es ambiguo."""
        return len(self.leaders) == 1


def _error_patterns(max_weight: int):
    """Todos los patrones de error de 24 bits de peso 0..max_weight."""
    for w in range(max_weight + 1):
        for posiciones in combinations(range(CW_BITS), w):
            e = 0
            for p in posiciones:
                e |= 1 << p
            yield w, e


@lru_cache(maxsize=None)
def coset_table(field: GF = GF2, max_weight: int = MAX_LEADER_WEIGHT) -> dict:
    """Construye la tabla ``síndrome -> Coset`` a partir de H.

    Recorre los patrones de error por peso creciente y, para cada
    síndrome, se queda con **todos** los patrones del primer peso en que
    aparece. Guardar todos y no solo uno es lo que después permite
    distinguir un coset corregible (líder único) de uno ambiguo.

    El resultado se cachea: construirlo cuesta unos segundos. No mutar el
    dict devuelto.

    Raises:
        RuntimeError: si la tabla no cubre los 4096 síndromes, lo que
            significaría que ``max_weight`` se quedó corto.
    """
    pesos: dict = {}
    lideres: dict = {}
    for w, e in _error_patterns(max_weight):
        s = syndrome(e, field)
        if s not in pesos:
            pesos[s] = w
            lideres[s] = [e]
        elif pesos[s] == w:
            lideres[s].append(e)

    esperados = 1 << MSG_BITS
    if len(pesos) != esperados:
        raise RuntimeError(
            f"La tabla cubre {len(pesos)} síndromes de {esperados}; "
            f"hace falta recorrer más allá de peso {max_weight}."
        )

    return {
        s: Coset(syndrome=s, weight=pesos[s], leaders=tuple(lideres[s]))
        for s in pesos
    }


def decode_by_table(rx: int, field: GF = GF2) -> DecodeResult:
    """Decodifica por tabla de síndromes, sin usar el algoritmo de casos.

    Corrige si y solo si el coste del síndrome tiene un líder único; si
    hay varios empatados, no hay forma de elegir y se declara no
    corregible. Es el oráculo contra el que se verifica
    :func:`golay.decoder.decode`.
    """
    s = syndrome(rx, field)
    coset = coset_table(field)[s]
    if not coset.unique:
        return DecodeResult(msg=0, err=0, corrected=False, uncorrectable=True,
                            syndrome=s, case=5)
    err = coset.leaders[0]
    cw = rx ^ err
    msg, _ = split_cw(cw)
    return DecodeResult(msg=msg, err=err, corrected=err != 0,
                        uncorrectable=False, syndrome=s, case=0)


def structure_summary(field: GF = GF2) -> Counter:
    """Resumen ``(peso, cantidad de líderes) -> cuántos cosets``.

    Para el Golay extendido tiene que dar ``{(0,1):1, (1,1):24, (2,1):276,
    (3,1):2024, (4,6):1771}``.
    """
    tabla = coset_table(field)
    return Counter((c.weight, len(c.leaders)) for c in tabla.values())
