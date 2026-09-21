"""
Álgebra matricial sobre GF(2^m): lo que el Trabajo Práctico 1 no cubría.

El TP1 dejó ``GF``, ``GFElement`` y ``GFPoly``, pero nada de matrices. El
Ejercicio 4 pide agregar producto vector-matriz, producto matriz-matriz y
peso de Hamming sobre esa misma clase de campo, y el Ejercicio 5 pide
construir G y H *con estas operaciones*, no a mano.

Convenciones
------------
- Un **vector** es una lista de ``GFElement``.
- Una **matriz** es una lista de filas, y cada fila es un vector.
- Los vectores son **fila**: ``vec_mat(v, M)`` calcula ``v · M``.
- Todo es función pura sobre listas; no se define ningún tipo nuevo. Los
  tipos ya los puso el TP1, acá faltaba el álgebra.

Nada de esto es específico de GF(2): funciona sobre cualquier ``GF``. El
peso de Hamming cuenta entradas no nulas, que también tiene sentido en
cualquier campo.
"""

from fec_algebra import GF, GFElement


# --------------------------------------------------------------- helpers
def _field_of(vec: list) -> GF:
    """Campo al que pertenece un vector no vacío."""
    if not vec:
        raise ValueError("No se puede inferir el campo de un vector vacío.")
    first = vec[0]
    if not isinstance(first, GFElement):
        raise ValueError(
            f"Se esperaba un vector de GFElement, se encontró {type(first).__name__}."
        )
    return first.field


def _check_rectangular(mat: list, nombre: str = "matriz") -> tuple:
    """Verifica que la matriz sea rectangular y devuelve ``(filas, columnas)``."""
    if not mat:
        raise ValueError(f"La {nombre} no puede estar vacía.")
    ancho = len(mat[0])
    if ancho == 0:
        raise ValueError(f"La {nombre} no puede tener filas vacías.")
    for k, fila in enumerate(mat):
        if len(fila) != ancho:
            raise ValueError(
                f"La {nombre} no es rectangular: la fila 0 tiene {ancho} "
                f"columnas y la fila {k} tiene {len(fila)}."
            )
    return len(mat), ancho


# ------------------------------------------------------- constructores
def zeros(rows: int, cols: int, field: GF) -> list:
    """Matriz nula de ``rows × cols`` sobre el campo dado."""
    if rows <= 0 or cols <= 0:
        raise ValueError(f"Dimensiones inválidas: {rows}×{cols}")
    return [[field(0) for _ in range(cols)] for _ in range(rows)]


def identity(n: int, field: GF) -> list:
    """Matriz identidad ``I_n`` sobre el campo dado."""
    if n <= 0:
        raise ValueError(f"n debe ser positivo, se recibió {n!r}")
    return [[field(1 if i == j else 0) for j in range(n)] for i in range(n)]


def hstack(left: list, right: list) -> list:
    """Concatena dos matrices lado a lado: ``[ left | right ]``.

    Es la operación con la que se arman G = [I | B] y H = [B | I].

    Raises:
        ValueError: si no tienen la misma cantidad de filas.
    """
    filas_i, _ = _check_rectangular(left, "matriz izquierda")
    filas_d, _ = _check_rectangular(right, "matriz derecha")
    if filas_i != filas_d:
        raise ValueError(
            f"No se pueden concatenar: {filas_i} filas contra {filas_d}."
        )
    return [list(a) + list(b) for a, b in zip(left, right)]


def transpose(mat: list) -> list:
    """Traspuesta de una matriz."""
    filas, cols = _check_rectangular(mat)
    return [[mat[i][j] for i in range(filas)] for j in range(cols)]


# ------------------------------------------------------------ suma
def vec_add(u: list, v: list) -> list:
    """Suma de vectores, componente a componente.

    En GF(2^m) sumar es XOR, así que esta es también la resta.

    Raises:
        ValueError: si los largos no coinciden.
    """
    if len(u) != len(v):
        raise ValueError(
            f"No se pueden sumar vectores de largo {len(u)} y {len(v)}."
        )
    return [a + b for a, b in zip(u, v)]


def mat_add(a: list, b: list) -> list:
    """Suma de matrices, entrada a entrada.

    Raises:
        ValueError: si las dimensiones no coinciden.
    """
    fa, ca = _check_rectangular(a, "primera matriz")
    fb, cb = _check_rectangular(b, "segunda matriz")
    if (fa, ca) != (fb, cb):
        raise ValueError(
            f"No se pueden sumar matrices de {fa}×{ca} y {fb}×{cb}."
        )
    return [vec_add(fila_a, fila_b) for fila_a, fila_b in zip(a, b)]


# ---------------------------------------------------------- productos
def vec_mat(v: list, mat: list) -> list:
    """Producto vector-matriz ``v · M``, con ``v`` vector fila.

    Si ``v`` tiene largo ``m`` y ``M`` es ``m × n``, el resultado es un
    vector de largo ``n`` con ``r[j] = sum_i v[i] * M[i][j]``.

    Se saltean los términos con ``v[i] = 0``, que en GF(2) es la mayoría:
    el producto se vuelve la suma de las filas seleccionadas por ``v``,
    que es exactamente como se hace la cuenta a mano en la Parte A.

    Raises:
        ValueError: si el largo de v no coincide con las filas de M.
    """
    filas, cols = _check_rectangular(mat)
    if len(v) != filas:
        raise ValueError(
            f"No se puede multiplicar un vector de largo {len(v)} "
            f"por una matriz de {filas}×{cols}."
        )
    field = _field_of(v)
    out = [field(0) for _ in range(cols)]
    for i, coef in enumerate(v):
        if int(coef) == 0:
            continue
        fila = mat[i]
        for j in range(cols):
            out[j] = out[j] + coef * fila[j]
    return out


def mat_mat(a: list, b: list) -> list:
    """Producto matriz-matriz ``A · B``.

    Raises:
        ValueError: si las columnas de A no coinciden con las filas de B.
    """
    fa, ca = _check_rectangular(a, "primera matriz")
    fb, cb = _check_rectangular(b, "segunda matriz")
    if ca != fb:
        raise ValueError(
            f"No se pueden multiplicar matrices de {fa}×{ca} y {fb}×{cb}."
        )
    return [vec_mat(fila, b) for fila in a]


# -------------------------------------------------------------- pesos
def weight(v: list) -> int:
    """Peso de Hamming: cantidad de entradas no nulas del vector."""
    return sum(1 for coef in v if int(coef) != 0)


def distance(u: list, v: list) -> int:
    """Distancia de Hamming entre dos vectores: ``w(u - v)``."""
    return weight(vec_add(u, v))


# ------------------------------------------------------- comparaciones
def is_zero(mat_o_vec: list) -> bool:
    """¿Es nula la matriz (o el vector)?"""
    if not mat_o_vec:
        return True
    if isinstance(mat_o_vec[0], GFElement):
        return all(int(coef) == 0 for coef in mat_o_vec)
    return all(is_zero(fila) for fila in mat_o_vec)


def equal(a: list, b: list) -> bool:
    """¿Son iguales dos matrices (o dos vectores)?"""
    if len(a) != len(b):
        return False
    if not a:
        return True
    if isinstance(a[0], GFElement):
        return all(x == y for x, y in zip(a, b))
    return all(equal(fa, fb) for fa, fb in zip(a, b))
