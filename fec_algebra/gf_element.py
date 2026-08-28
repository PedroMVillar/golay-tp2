"""
Clase GFElement: un elemento vivo de un campo GF(2^m). Es un entero en
[0, 2^m - 1] que sabe a qué campo pertenece y sobrecarga los operadores
aritméticos de Python, delegando el cálculo real en la instancia de GF
correspondiente.
"""

from .exceptions import GFFieldMismatchError


class GFElement:
    """Un elemento de un campo GF(2^m).

    No se instancia directamente: se crea llamando a la instancia de GF,
    por ejemplo field(0x53), para que el valor quede validado y asociado
    al campo correcto.

    Args:
        field: instancia de GF a la que pertenece este elemento.
        value: entero en [0, 2^m - 1] que representa el elemento.
    """

    def __init__(self, field, value: int):
        self.field = field
        self.value = value

    def _check_same_field(self, other: "GFElement") -> None:
        """Chequea que other sea del mismo campo que self.

        Raises:
            GFFieldMismatchError: si los campos no coinciden.
        """
        if not isinstance(other, GFElement) or other.field != self.field:
            raise GFFieldMismatchError(
                f"No se puede operar entre elementos de campos distintos: "
                f"{self.field!r} vs {getattr(other, 'field', type(other))!r}"
            )

    def __add__(self, other: "GFElement") -> "GFElement":
        self._check_same_field(other)
        return GFElement(self.field, self.field.add(self.value, other.value))

    def __mul__(self, other: "GFElement") -> "GFElement":
        self._check_same_field(other)
        return GFElement(self.field, self.field.multiply(self.value, other.value))

    def __invert__(self) -> "GFElement":
        """Inverso multiplicativo, con la sintaxis ~a.

        Raises:
            GFZeroDivisionError: si self es el elemento 0.
        """
        return GFElement(self.field, self.field.inverse(self.value))

    def inverse(self) -> "GFElement":
        """Lo mismo que ~self, para quien prefiera a.inverse() en vez del operador."""
        return ~self

    def __truediv__(self, other: "GFElement") -> "GFElement":
        """División, con la sintaxis a / b.

        Raises:
            GFZeroDivisionError: si other es el elemento 0.
        """
        self._check_same_field(other)
        return GFElement(self.field, self.field.divide(self.value, other.value))

    def __pow__(self, n: int) -> "GFElement":
        """Potencia, con la sintaxis a ** n, para n >= 0."""
        return GFElement(self.field, self.field.power(self.value, n))

    def __eq__(self, other) -> bool:
        """Dos GFElement son iguales si son del mismo campo y tienen el mismo valor."""
        if not isinstance(other, GFElement):
            return NotImplemented
        return self.field == other.field and self.value == other.value

    def __hash__(self) -> int:
        # necesario para meter GFElement en sets/dicts, y para que sea
        # consistente con __eq__
        return hash((self.field, self.value))

    def __int__(self) -> int:
        """Devuelve el entero crudo con int(elemento)."""
        return self.value

    def __bool__(self) -> bool:
        """Permite usar un GFElement en un if directamente: solo el elemento 0 es False."""
        return self.value != 0

    def __repr__(self) -> str:
        width = (self.field.m + 3) // 4  # dígitos hexa que hacen falta para m bits
        return f"GFElement({self.value:#0{width + 2}x}, {self.field!r})"
