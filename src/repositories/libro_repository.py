from typing import Optional, List

from ..models.libro import Libro
from ..exceptions import LibroNoEncontradoError, LibroYaExisteError


class LibroRepository:
    def __init__(self):
        self._libros: dict = {}

    def agregar(self, libro: Libro) -> None:
        if libro.isbn in self._libros:
            raise LibroYaExisteError(
                f"Ya existe un libro con ISBN '{libro.isbn}'"
            )
        self._libros[libro.isbn] = libro

    def obtener_por_isbn(self, isbn: str) -> Optional[Libro]:
        return self._libros.get(isbn.strip())

    def obtener_todos(self) -> List[Libro]:
        return list(self._libros.values())

    def obtener_disponibles(self) -> List[Libro]:
        return [l for l in self._libros.values() if l.esta_disponible()]

    def eliminar(self, isbn: str) -> None:
        isbn = isbn.strip()
        if isbn not in self._libros:
            raise LibroNoEncontradoError(
                f"No se encontró el libro con ISBN '{isbn}'"
            )
        del self._libros[isbn]

    def existe(self, isbn: str) -> bool:
        return isbn.strip() in self._libros

    def cantidad(self) -> int:
        return len(self._libros)
