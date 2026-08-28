"""
Clase GFPoly: un polinomio con coeficientes en un campo GF(2^m). Los
coeficientes se guardan como una tupla de GFElement, en orden decreciente
de grado: (a_n, ..., a_1, a_0).

Invariante: la representación interna nunca tiene ceros a la izquierda,
salvo el polinomio nulo, que se guarda como (field(0),).
"""

from .gf_element import GFElement
from .exceptions import GFFieldMismatchError, GFValueError, GFZeroDivisionError


class GFPoly:
    """Un polinomio con coeficientes en GF(2^m).

    Args:
        field: instancia de GF sobre la que están definidos los coeficientes.
        coefficients: lista o tupla de coeficientes en orden decreciente de
            grado, [a_n, ..., a_1, a_0]. Cada coeficiente puede ser un
            GFElement del mismo field, o un int (se convierte solo, vía
            field()).

    Raises:
        GFValueError: si coefficients está vacía, o algún coeficiente no
            es un elemento válido del campo.
        GFFieldMismatchError: si algún coeficiente es un GFElement de un
            campo distinto de field.
    """

    def __init__(self, field, coefficients):
        if coefficients is None or len(coefficients) == 0:
            raise GFValueError(
                "coefficients no puede estar vacío; use GFPoly.zero(field) "
                "para representar el polinomio nulo."
            )

        self.field = field

        normalized = []
        for c in coefficients:
            if isinstance(c, GFElement):
                if c.field != field:
                    raise GFFieldMismatchError(
                        f"Coeficiente {c!r} pertenece a un campo distinto de {field!r}."
                    )
                normalized.append(c)
            elif isinstance(c, int):
                normalized.append(field(c))  # valida rango
            else:
                raise GFValueError(
                    f"Coeficiente inválido {c!r}: debe ser GFElement o int."
                )

        self._coeffs = tuple(self._strip_leading_zeros(normalized, field))

    @staticmethod
    def _strip_leading_zeros(coefficients, field):
        """Saca los coeficientes nulos del principio de la lista (los de
        mayor grado), dejando al menos uno: el polinomio nulo siempre
        queda como [field(0)], nunca como lista vacía."""
        i = 0
        while i < len(coefficients) - 1 and coefficients[i].value == 0:
            i += 1
        return coefficients[i:]

    @classmethod
    def zero(cls, field) -> "GFPoly":
        """El polinomio nulo (0) sobre el campo dado."""
        return cls(field, [field(0)])

    @classmethod
    def from_roots(cls, field, roots) -> "GFPoly":
        """Construye el polinomio mónico cuyas raíces son exactamente las
        dadas: el producto de (x - r_i) para cada r_i en roots.

        En GF(2^m) restar es lo mismo que sumar (característica 2, Lin &
        Costello cap. 2), así que (x - r_i) se arma directamente como el
        polinomio de coeficientes [1, r_i].

        Si roots está vacío, devuelve el polinomio constante 1 (producto
        vacío, convención matemática de siempre).

        Esto conecta con lo que hace el libro para construir el polinomio
        mínimo de un elemento a partir de su clase de conjugación bajo
        Frobenius (elevar al cuadrado repetidamente): from_roots es la
        versión general de esa idea, para cualquier conjunto de raíces,
        no solo conjugadas entre sí.

        Args:
            field: campo GF(2^m) sobre el que se construye el polinomio.
            roots: colección de GFElement (o int) que van a ser las raíces.
        """
        result = cls(field, [field(1)])
        for r in roots:
            r_elem = field(r) if not isinstance(r, GFElement) else r
            factor = cls(field, [field(1), r_elem])  # (x - r) = (x + r) acá
            result = result * factor
        return result

    @property
    def degree(self) -> int:
        """Grado del polinomio. El polinomio nulo tiene grado -1, como se usa siempre en álgebra."""
        if len(self._coeffs) == 1 and self._coeffs[0].value == 0:
            return -1
        return len(self._coeffs) - 1

    def _check_same_field(self, other: "GFPoly") -> None:
        """Chequea que other esté definido sobre el mismo campo que self.

        Raises:
            GFFieldMismatchError: si los campos no coinciden.
        """
        if not isinstance(other, GFPoly) or other.field != self.field:
            raise GFFieldMismatchError(
                f"No se puede operar entre polinomios de campos distintos: "
                f"{self.field!r} vs {getattr(other, 'field', type(other))!r}"
            )

    def __add__(self, other: "GFPoly") -> "GFPoly":
        self._check_same_field(other)
        n = max(len(self._coeffs), len(other._coeffs))
        zero = self.field(0)
        a = (zero,) * (n - len(self._coeffs)) + self._coeffs
        b = (zero,) * (n - len(other._coeffs)) + other._coeffs
        result = [x + y for x, y in zip(a, b)]
        return GFPoly(self.field, result)

    def __mul__(self, other: "GFPoly") -> "GFPoly":
        self._check_same_field(other)
        zero = self.field(0)

        if self.degree == -1 or other.degree == -1:
            return GFPoly.zero(self.field)

        # convolución de coeficientes en orden decreciente: si a tiene
        # grado n y b grado k, el producto da grado n + k
        result_len = len(self._coeffs) + len(other._coeffs) - 1
        result = [zero] * result_len
        for i, a_coef in enumerate(self._coeffs):
            if a_coef.value == 0:
                continue
            for j, b_coef in enumerate(other._coeffs):
                result[i + j] = result[i + j] + a_coef * b_coef
        return GFPoly(self.field, result)

    def __divmod__(self, other: "GFPoly"):
        """División polinómica entera: devuelve (cociente, resto).
        Permite usar el divmod(p1, p2) de Python.

        Es el algoritmo de división larga de siempre, adaptado a que los
        coeficientes viven en GF(2^m): "restar" es sumar (XOR), y dividir
        por el coeficiente principal del divisor es multiplicar por su
        inverso.

        Raises:
            GFZeroDivisionError: si other es el polinomio nulo.
        """
        self._check_same_field(other)
        if other.degree == -1:
            raise GFZeroDivisionError("No se puede dividir por el polinomio nulo.")

        if self.degree < other.degree:
            return GFPoly.zero(self.field), self

        remainder = list(self._coeffs)  # orden decreciente, copia mutable
        divisor = other._coeffs
        lead_inv = divisor[0].inverse()
        quotient = [self.field(0)] * (self.degree - other.degree + 1)

        for i in range(len(quotient)):
            if remainder[i].value != 0:
                factor = remainder[i] * lead_inv
                quotient[i] = factor
                for j, d_coef in enumerate(divisor):
                    remainder[i + j] = remainder[i + j] + factor * d_coef

        return GFPoly(self.field, quotient), GFPoly(self.field, remainder)

    def __floordiv__(self, other: "GFPoly") -> "GFPoly":
        """Cociente de la división entera, con p1 // p2."""
        quotient, _ = divmod(self, other)
        return quotient

    def __mod__(self, other: "GFPoly") -> "GFPoly":
        """Resto de la división entera, con p1 % p2."""
        _, remainder = divmod(self, other)
        return remainder

    def scale(self, scalar: GFElement) -> "GFPoly":
        """Multiplica todos los coeficientes por un escalar del campo."""
        scalar = self.field(scalar) if not isinstance(scalar, GFElement) else scalar
        return GFPoly(self.field, [c * scalar for c in self._coeffs])

    def evaluate(self, x: GFElement) -> GFElement:
        """Evalúa el polinomio en x, con el método de Horner:
        p(x) = (...((a_n * x + a_{n-1}) * x + a_{n-2}) * x + ...) * x + a_0
        Con esto alcanzan len(coeffs) - 1 multiplicaciones, en vez de
        calcular cada potencia de x por separado."""
        x = self.field(x) if not isinstance(x, GFElement) else x
        result = self.field(0)
        for coef in self._coeffs:
            result = result * x + coef
        return result

    def __call__(self, x: GFElement) -> GFElement:
        """Atajo para poder escribir poly(x) en vez de poly.evaluate(x)."""
        return self.evaluate(x)

    def __getitem__(self, index: int) -> GFElement:
        """Coeficiente de x^index; poly[0] es el término independiente.
        Si index supera el grado, devuelve field(0)."""
        pos_from_end = index  # x^0 queda al final de _coeffs (orden decreciente)
        if pos_from_end < 0 or pos_from_end >= len(self._coeffs):
            return self.field(0)
        return self._coeffs[len(self._coeffs) - 1 - pos_from_end]

    def __eq__(self, other) -> bool:
        """Dos GFPoly son iguales si están sobre el mismo campo y tienen los mismos coeficientes."""
        if not isinstance(other, GFPoly):
            return NotImplemented
        return self.field == other.field and self._coeffs == other._coeffs

    def __hash__(self) -> int:
        return hash((self.field, self._coeffs))

    def __repr__(self) -> str:
        coefs = ", ".join(hex(c.value) for c in self._coeffs)
        return f"GFPoly([{coefs}], {self.field!r})"
