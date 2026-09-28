"""
Genera las tablas largas de la Parte A en gen/, para no copiar a mano
todos esos números al .tex.
"""
import os

B = [0x98F, 0x4E7, 0x357, 0xBE2, 0xDD1, 0x7CC,
     0x53D, 0x2BE, 0x87B, 0xE74, 0xF1A, 0xEA9]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen")
os.makedirs(OUT, exist_ok=True)


def w(x):
    return bin(x).count("1")


def bits(x, n=12):
    return format(x, "0{}b".format(n))


def nib(x, n=12):
    s = bits(x, n)
    return r"\,".join(s[i:i + 4] for i in range(0, len(s), 4))


def tt(x, n=12):
    return r"\texttt{" + nib(x, n) + "}"


def mulB(v):
    r = 0
    for i in range(12):
        if (v >> (11 - i)) & 1:
            r ^= B[i]
    return r


def rows_of(v):
    return [i for i in range(12) if (v >> (11 - i)) & 1]


def enc(m):
    return (m << 12) | mulB(m)


def syn(r):
    return mulB(r >> 12) ^ (r & 0xFFF)


def write(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("% generado por gen_parte_a.py -- no editar a mano\n")
        f.write(body)
        f.write("\n")
    print("  ->", os.path.join("gen", name))


L = [r"\begin{tabular}{@{}llc@{\hspace{2.5em}}llc@{}}", r"\toprule",
     r"fila & hex & binario & fila & hex & binario \\", r"\midrule"]
for i in range(6):
    j = i + 6
    L.append(r"$b_{%d}$ & \texttt{%03X} & %s & $b_{%d}$ & \texttt{%03X} & %s \\"
             % (i, B[i], tt(B[i]), j, B[j], tt(B[j])))
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_b.tex", "\n".join(L))


def matriz_bloque(left, right, label):
    L = [r"\begin{tabular}{@{}r@{\;\;}c@{\;\;}c@{}}"]
    for i in range(12):
        L.append(r"$%s_{%d}$ & \texttt{%s} & \texttt{%s} \\"
                 % (label, i, bits(left[i]), bits(right[i])))
    L.append(r"\end{tabular}")
    return "\n".join(L)


I12 = [1 << (11 - i) for i in range(12)]
write("matriz_g.tex", matriz_bloque(I12, B, "g"))
write("matriz_h.tex", matriz_bloque(B, I12, "h"))


cols = []
for j in range(12):
    c = 0
    for i in range(12):
        if (B[i] >> (11 - j)) & 1:
            c |= 1 << (11 - i)
    cols.append(c)
assert cols == B, "B no es simetrica"

L = [r"\begin{tabular}{@{}ccc@{\hspace{2.5em}}ccc@{}}", r"\toprule",
     r"$j$ & columna $j$ & $b_j$ & $j$ & columna $j$ & $b_j$ \\",
     r"\midrule"]
for j in range(6):
    k = j + 6
    L.append(r"%d & %s & %s & %d & %s & %s \\"
             % (j, tt(cols[j]), tt(B[j]), k, tt(cols[k]), tt(B[k])))
L += [r"\bottomrule", r"\end{tabular}"]
write("tabla_simetria.tex", "\n".join(L))


W = [[w(B[i] & B[j]) for j in range(12)] for i in range(12)]
P = [[W[i][j] % 2 for j in range(12)] for i in range(12)]
assert all(P[i][j] == (1 if i == j else 0)
           for i in range(12) for j in range(12)), "B^2 distinto de I"

L = [r"\begin{tabular}{@{}r|*{12}{c}@{}}",
     r"$w(b_i\wedge b_j)$ & " + " & ".join(r"$\mathbf{%d}$" % j for j in range(12)) + r" \\",
     r"\midrule"]
for i in range(12):
    celdas = []
    for j in range(12):
        if j < i:
            celdas.append(r"\textcolor{gris}{%d}" % W[i][j])
        elif j == i:
            celdas.append(r"\textbf{%d}" % W[i][j])
        else:
            celdas.append(str(W[i][j]))
    L.append(r"$\mathbf{%d}$ & " % i + " & ".join(celdas) + r" \\")
L.append(r"\end{tabular}")
write("tabla_bcuadrado.tex", "\n".join(L))

L = []
for (i, j) in [(0, 0), (0, 1), (3, 7)]:
    a, b = B[i], B[j]
    L.append(r"\begin{align*}")
    L.append(r"b_{%d} &= \texttt{%s} \\" % (i, nib(a)))
    L.append(r"b_{%d} &= \texttt{%s} \\" % (j, nib(b)))
    L.append(r"b_{%d}\wedge b_{%d} &= \texttt{%s}"
             r" \quad\Longrightarrow\quad w = %d \equiv %d \!\pmod 2"
             % (i, j, nib(a & b), w(a & b), w(a & b) % 2))
    L.append(r"\end{align*}")
write("ejemplos_bcuadrado.tex", "\n".join(L))


def cadena_xor(v, etiqueta):
    idx = rows_of(v)
    L = [r"\begin{tabular}{@{}r@{\;\;}l@{\;\;}l@{}}"]
    acc = 0
    for k, i in enumerate(idx):
        signo = "" if k == 0 else r"$\oplus$"
        L.append(r"%s & $b_{%d}$ & \texttt{%s} \\" % (signo, i, nib(B[i])))
        acc ^= B[i]
        if 0 < k < len(idx) - 1:
            L.append(r"\cmidrule(lr){2-3}")
            L.append(r" & & \texttt{%s} \\" % nib(acc))
    L.append(r"\cmidrule(lr){2-3}")
    L.append(r" & $%s$ & \texttt{%s} \;$=$\; \texttt{%03X} \\"
             % (etiqueta, nib(acc), acc))
    L.append(r"\end{tabular}")
    return "\n".join(L), acc


msg = 0xA5C
cad, p = cadena_xor(msg, "p")
assert p == 0x9A5, hex(p)
write("xor_codificacion.tex", cad)
v_ej = enc(msg)


def tabla_busqueda(x, simbolo):
    L = [r"\begin{tabular}{@{}cccc@{}}", r"\toprule",
         r"$i$ & $b_i$ & $%s\oplus b_i$ & $w$ \\" % simbolo, r"\midrule"]
    hit = None
    for i in range(12):
        y = x ^ B[i]
        peso = w(y)
        if peso <= 2:
            celda = r"$\mathbf{%d}$ $\leftarrow$" % peso
            if hit is None:
                hit = i
        else:
            celda = str(peso)
        L.append(r"%d & \texttt{%s} & \texttt{%s} & %s \\"
                 % (i, nib(B[i]), nib(y), celda))
    L += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(L), hit


def decodificar(r):
    tr = {"r": r, "rm": r >> 12, "rp": r & 0xFFF}
    tr["mB"] = mulB(r >> 12)
    s = tr["mB"] ^ (r & 0xFFF)
    tr["s"], tr["ws"] = s, w(s)
    if tr["ws"] <= 3:
        tr["caso"], tr["e"] = 1, s
        return tr
    tab2, i2 = tabla_busqueda(s, "s")
    tr["tabla2"] = tab2
    if i2 is not None:
        tr["caso"], tr["i"] = 2, i2
        tr["e"] = ((1 << (11 - i2)) << 12) | (s ^ B[i2])
        return tr
    q = mulB(s)
    tr["q"], tr["wq"] = q, w(q)
    if tr["wq"] <= 3:
        tr["caso"], tr["e"] = 3, q << 12
        return tr
    tab4, i4 = tabla_busqueda(q, "q")
    tr["tabla4"] = tab4
    if i4 is not None:
        tr["caso"], tr["i"] = 4, i4
        tr["e"] = ((q ^ B[i4]) << 12) | (1 << (11 - i4))
        return tr
    tr["caso"] = 5
    return tr


resumen = []
for nombre, r in (("rA", 0xA5D9A6), ("rB", 0xA5F9A4), ("rC", 0xA5C9AA)):
    tr = decodificar(r)
    L = []

    cad, mB = cadena_xor(tr["rm"], r"B\,r_{[23:12]}")
    assert mB == tr["mB"]
    L += [r"\newcommand{\%sXor}{%%" % nombre, cad, "}"]

    L += [r"\newcommand{\%sSind}{%%" % nombre,
          r"\begin{tabular}{@{}r@{\;\;}l@{\;\;}l@{}}",
          r" & $B\,r_{[23:12]}$ & \texttt{%s} \\" % nib(tr["mB"]),
          r"$\oplus$ & $r_{[11:0]}$ & \texttt{%s} \\" % nib(tr["rp"]),
          r"\midrule",
          r" & $s$ & \texttt{%s} \;$=$\; \texttt{%03X} \\" % (nib(tr["s"]), tr["s"]),
          r"\end{tabular}", "}"]

    L += [r"\newcommand{\%sPesoS}{%d}" % (nombre, tr["ws"])]

    if "tabla2" in tr:
        L += [r"\newcommand{\%sTablaDos}{%%" % nombre, tr["tabla2"], "}"]
    if "q" in tr:
        cadq, qq = cadena_xor(tr["s"], "q")
        assert qq == tr["q"]
        L += [r"\newcommand{\%sQ}{%%" % nombre, cadq, "}",
              r"\newcommand{\%sPesoQ}{%d}" % (nombre, tr["wq"])]
    if "tabla4" in tr:
        L += [r"\newcommand{\%sTablaCuatro}{%%" % nombre, tr["tabla4"], "}"]

    L.append(r"\newcommand{\%sRes}{%%" % nombre)
    if tr["caso"] == 5:
        L.append(r"---")
    else:
        e, vv = tr["e"], r ^ tr["e"]
        assert syn(vv) == 0
        L += [r"\begin{tabular}{@{}r@{\;\;}l@{\;\;}l@{}}",
              r" & $r$ & \texttt{%s} \\" % nib(r, 24),
              r"$\oplus$ & $e$ & \texttt{%s} \\" % nib(e, 24),
              r"\midrule",
              r" & $v$ & \texttt{%s} \;$=$\; \texttt{%06X} \\" % (nib(vv, 24), vv),
              r"\end{tabular}"]
    L.append("}")

    write("dec_%s.tex" % nombre, "\n".join(L))
    resumen.append((nombre, r, tr))
    print("     %s = %06X  ->  s = %03X, caso %d" % (nombre, r, tr["s"], tr["caso"]))


L = [r"\newcommand{\parEj}{\texttt{%03X}}" % p,
     r"\newcommand{\cwEj}{\texttt{%06X}}" % v_ej]
write("constantes.tex", "\n".join(L))

print("\nchequeos: B simetrica OK | B^2 = I OK | "
      "v = %06X con sindrome %03X" % (v_ej, syn(v_ej)))
