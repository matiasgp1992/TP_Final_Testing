from dataclasses import dataclass, field
from enum import Enum

from .autor import Autor


class EstadoLibro(Enum):
    DISPONIBLE = "Disponible"
    PRESTADO = "Prestado"


@dataclass
class Libro:
    isbn: str
    titulo: str
    editorial: str
    autor: Autor
    estado: EstadoLibro = field(default=EstadoLibro.DISPONIBLE)

    def __post_init__(self):
        if not self.isbn or not self.isbn.strip():
            raise ValueError("El ISBN no puede estar vacío")
        if not self.titulo or not self.titulo.strip():
            raise ValueError("El título no puede estar vacío")
        if not self.editorial or not self.editorial.strip():
            raise ValueError("La editorial no puede estar vacía")
        self.isbn = self.isbn.strip()
        self.titulo = self.titulo.strip()
        self.editorial = self.editorial.strip()

    def esta_disponible(self) -> bool:
        return self.estado == EstadoLibro.DISPONIBLE

    def marcar_prestado(self) -> None:
        self.estado = EstadoLibro.PRESTADO

    def marcar_disponible(self) -> None:
        self.estado = EstadoLibro.DISPONIBLE

    def __eq__(self, other):
        if not isinstance(other, Libro):
            return False
        return self.isbn == other.isbn

    def __hash__(self):
        return hash(self.isbn)
