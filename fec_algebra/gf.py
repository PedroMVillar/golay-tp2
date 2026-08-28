"""
Clase GF: representa un campo de Galois GF(2^m).

GF funciona como una fábrica de GFElement: guarda el orden m y el
polinomio primitivo, y sabe reducir el resultado de una multiplicación
módulo ese polinomio. Los elementos "vivos" del campo son instancias de
GFElement, que en realidad delegan toda la aritmética acá adentro.

Cada elemento se representa como un entero en [0, 2^m - 1]: se toman
sus m coeficientes binarios (b_{m-1}, ..., b_1, b_0) y se leen como un
número en base 2 (más detalle en GFElement y en el enunciado del TP).
"""

from .gf_element import GFElement
from .exceptions import GFZeroDivisionError, GFValueError


class GF:
    """El campo de Galois GF(2^m).

    Args:
        m: orden del campo (tiene 2^m elementos).
        primitive_poly: polinomio primitivo P(x) que define la reducción,
            representado como entero de m bits. Debe cumplir
            0 <= primitive_poly < 2^m.

    Raises:
        GFValueError: si m no es un entero positivo, o si primitive_poly
            no entra en el rango representable en m bits.

    GF(2^m) se construye como polinomios módulo un polinomio irreducible
    de grado m sobre GF(2). Para que un elemento termine generando todo
    el grupo multiplicativo, ese polinomio además tiene que ser primitivo:
    no alcanza con que sea irreducible. Esta clase no verifica primitividad,
    ni siquiera irreducibilidad: confía en que el primitive_poly que le
    llega ya es correcto, igual que lo da como dato el enunciado del TP.
    """

    def __init__(self, m: int, primitive_poly: int):
        if not isinstance(m, int) or m <= 0:
            raise GFValueError(f"m debe ser un entero positivo, se recibió {m!r}")
        if not isinstance(primitive_poly, int) or not (0 <= primitive_poly < (1 << m)):
            raise GFValueError(
                f"primitive_poly debe ser un entero en [0, {(1 << m) - 1}] "
                f"(m={m} bits, sin el término x^m), se recibió {primitive_poly!r}"
            )

        self.m = m
        self.primitive_poly = primitive_poly
        # término x^m implícito del primitivo, sirve para detectar cuándo
        # el producto se pasa de grado y hay que reducir
        self._reduction_bit = 1 << m

    @property
    def order(self) -> int:
        """Cantidad de elementos del campo (2^m)."""
        return 1 << self.m

    def __call__(self, value: int) -> GFElement:
        """Crea un GFElement a partir de un entero en [0, 2^m - 1].
        Permite escribir directamente field(0x53).

        Si value ya es un GFElement de este mismo campo, se devuelve
        tal cual (así una función puede aceptar tanto int como GFElement
        sin distinguir casos).

        Raises:
            GFValueError: si value está fuera de rango, o es un
                GFElement de otro campo.
        """
        if isinstance(value, GFElement):
            if value.field != self:
                raise GFValueError(
                    "No se puede crear un elemento a partir de un GFElement "
                    "que pertenece a otro campo."
                )
            return value

        if not isinstance(value, int) or not (0 <= value < self.order):
            raise GFValueError(
                f"El valor debe ser un entero en [0, {self.order - 1}], "
                f"se recibió {value!r}"
            )
        return GFElement(self, value)

    # operaciones de bajo nivel sobre enteros crudos (no GFElement);
    # GFElement delega en estos métodos para implementar sus operadores

    def add(self, a: int, b: int) -> int:
        """Suma dos elementos como enteros crudos. En GF(2^m) sumar es hacer XOR bit a bit."""
        return a ^ b

    def multiply(self, a: int, b: int) -> int:
        """Producto de dos elementos (enteros crudos), reducido módulo el polinomio primitivo.

        Es la multiplicación clásica "shift-and-xor" de polinomios sobre
        GF(2): se recorre bit a bit el segundo operando, por cada bit en
        1 se hace XOR con el primero (desplazado), y si en algún punto
        el resultado se pasa de grado m-1, se reduce haciendo XOR con el
        primitivo desplazado a la posición que corresponde.
        """
        result = 0
        x, y = a, b
        for _ in range(self.m):
            if y & 1:
                result ^= x
            y >>= 1
            carry = x & (1 << (self.m - 1))
            x <<= 1
            if carry:
                # x se pasó de grado m-1, hay que reducir con el
                # primitivo (el término x^m se cancela solo)
                x ^= (1 << self.m) | self.primitive_poly
                x &= self.order - 1
        return result & (self.order - 1)

    def inverse(self, a: int) -> int:
        """Inverso multiplicativo de a (entero crudo).

        Se apoya en que el orden de un elemento no nulo siempre divide
        2^m - 1, y en particular a^(2^m - 1) == 1 para todo a != 0 (es
        la versión de Fermat para cuerpos finitos, Lin & Costello cap. 2).
        De ahí sale directo que a^(2^m - 2) == a^-1.

        Raises:
            GFZeroDivisionError: si a == 0 (el 0 no tiene inverso).
        """
        if a == 0:
            raise GFZeroDivisionError(
                "El elemento 0 no tiene inverso multiplicativo en GF(2^m)."
            )
        # a^(orden - 1) == 1 para todo a != 0, entonces a^(orden - 2) == a^-1
        return self.power(a, self.order - 2)

    def divide(self, a: int, b: int) -> int:
        """División a / b : a * b^-1.

        Raises:
            GFZeroDivisionError: si b == 0.
        """
        if b == 0:
            raise GFZeroDivisionError("No se puede dividir por el elemento 0.")
        return self.multiply(a, self.inverse(b))

    def power(self, a: int, n: int) -> int:
        """Potencia a^n por square-and-multiply, para n >= 0."""
        if not isinstance(n, int) or n < 0:
            raise GFValueError(f"El exponente debe ser un entero >= 0, se recibió {n!r}")

        result = 1  # neutro multiplicativo
        base = a
        exponent = n
        while exponent > 0:
            if exponent & 1:
                result = self.multiply(result, base)
            base = self.multiply(base, base)
            exponent >>= 1
        return result

    def __eq__(self, other) -> bool:
        """Dos GF son iguales si tienen el mismo m y el mismo polinomio primitivo."""
        if not isinstance(other, GF):
            return NotImplemented
        return self.m == other.m and self.primitive_poly == other.primitive_poly

    def __hash__(self) -> int:
        return hash((self.m, self.primitive_poly))

    def __repr__(self) -> str:
        return f"GF(2^{self.m}, primitive_poly={hex(self.primitive_poly)})"
