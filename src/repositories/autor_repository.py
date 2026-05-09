from typing import Optional, List

from ..models.autor import Autor
from ..exceptions import AutorNoEncontradoError, AutorYaExisteError


class AutorRepository:
    def __init__(self):
        self._autores: dict = {}

    def _clave(self, nombre: str, apellido: str) -> str:
        return f"{nombre.strip().lower()}_{apellido.strip().lower()}"

    def agregar(self, autor: Autor) -> None:
        clave = self._clave(autor.nombre, autor.apellido)
        if clave in self._autores:
            raise AutorYaExisteError(
                f"Ya existe un autor con nombre '{autor.nombre_completo()}'"
            )
        self._autores[clave] = autor

    def buscar(self, nombre: str, apellido: str) -> Optional[Autor]:
        return self._autores.get(self._clave(nombre, apellido))

    def obtener_todos(self) -> List[Autor]:
        return list(self._autores.values())

    def eliminar(self, nombre: str, apellido: str) -> None:
        clave = self._clave(nombre, apellido)
        if clave not in self._autores:
            raise AutorNoEncontradoError(
                f"No se encontró el autor '{nombre} {apellido}'"
            )
        del self._autores[clave]

    def existe(self, nombre: str, apellido: str) -> bool:
        return self._clave(nombre, apellido) in self._autores

    def cantidad(self) -> int:
        return len(self._autores)
