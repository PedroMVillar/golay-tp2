"""
Álgebra matricial sobre GF(2^m), lo que le faltaba a la librería del TP1.

Los vectores son listas de GFElement y las matrices listas de filas.
"""

from fec_algebra import GFElement


def identity(n, field):
    return [[field(1 if i == j else 0) for j in range(n)] for i in range(n)]


def hstack(left, right):
    return [list(a) + list(b) for a, b in zip(left, right)]


def transpose(mat):
    return [list(col) for col in zip(*mat)]


def vec_add(u, v):
    if len(u) != len(v):
        raise ValueError("los vectores tienen distinto largo")
    return [a + b for a, b in zip(u, v)]


def vec_mat(v, mat):
    # v es vector fila: v · M
    if len(v) != len(mat):
        raise ValueError("dimensiones incompatibles")
    out = [v[0].field(0)] * len(mat[0])
    for i, coef in enumerate(v):
        if int(coef) == 0:
            continue
        out = [o + coef * m for o, m in zip(out, mat[i])]
    return out


def mat_mat(a, b):
    if len(a[0]) != len(b):
        raise ValueError("dimensiones incompatibles")
    return [vec_mat(fila, b) for fila in a]


def weight(v):
    return sum(1 for coef in v if int(coef) != 0)


def is_zero(m):
    if isinstance(m[0], GFElement):
        return all(int(x) == 0 for x in m)
    return all(is_zero(fila) for fila in m)


def equal(a, b):
    return len(a) == len(b) and all(
        x == y if isinstance(x, GFElement) else equal(x, y) for x, y in zip(a, b)
    )
