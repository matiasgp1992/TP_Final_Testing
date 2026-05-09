from typing import List, Optional

from ..models.autor import Autor
from ..models.libro import Libro
from ..models.cliente import Cliente
from ..models.prestamo import Prestamo
from ..repositories.autor_repository import AutorRepository
from ..repositories.libro_repository import LibroRepository
from ..repositories.cliente_repository import ClienteRepository
from ..repositories.prestamo_repository import PrestamoRepository
from ..exceptions import (
    AutorNoEncontradoError,
    LibroNoEncontradoError,
    LibroPrestadoError,
    ClienteNoEncontradoError,
    ClienteInactivoError,
)


class BibliotecaService:
    def __init__(
        self,
        autor_repo: AutorRepository,
        libro_repo: LibroRepository,
        cliente_repo: ClienteRepository,
        prestamo_repo: PrestamoRepository,
    ):
        self._autores = autor_repo
        self._libros = libro_repo
        self._clientes = cliente_repo
        self._prestamos = prestamo_repo

    # ── Autores ──────────────────────────────────────────────────────────────

    def agregar_autor(self, nombre: str, apellido: str, nacionalidad: str = "") -> Autor:
        autor = Autor(nombre=nombre, apellido=apellido, nacionalidad=nacionalidad)
        self._autores.agregar(autor)
        return autor

    def obtener_autores(self) -> List[Autor]:
        return self._autores.obtener_todos()

    def buscar_autor(self, nombre: str, apellido: str) -> Optional[Autor]:
        return self._autores.buscar(nombre, apellido)

    # ── Libros ───────────────────────────────────────────────────────────────

    def agregar_libro(
        self, isbn: str, titulo: str, editorial: str,
        nombre_autor: str, apellido_autor: str
    ) -> Libro:
        autor = self._autores.buscar(nombre_autor, apellido_autor)
        if autor is None:
            raise AutorNoEncontradoError(
                f"No se encontró el autor '{nombre_autor} {apellido_autor}'. "
                "Regístrelo primero."
            )
        libro = Libro(isbn=isbn, titulo=titulo, editorial=editorial, autor=autor)
        self._libros.agregar(libro)
        return libro

    def dar_de_baja_libro(self, isbn: str) -> None:
        libro = self._libros.obtener_por_isbn(isbn)
        if libro is None:
            raise LibroNoEncontradoError(f"No se encontró el libro con ISBN '{isbn}'")
        if not libro.esta_disponible():
            raise LibroPrestadoError(
                f"El libro '{libro.titulo}' está prestado y no puede darse de baja"
            )
        self._libros.eliminar(isbn)

    def obtener_libros(self) -> List[Libro]:
        return self._libros.obtener_todos()

    def obtener_libro(self, isbn: str) -> Optional[Libro]:
        return self._libros.obtener_por_isbn(isbn)

    def obtener_libros_disponibles(self) -> List[Libro]:
        return self._libros.obtener_disponibles()

    # ── Clientes ─────────────────────────────────────────────────────────────

    def agregar_cliente(self, dni: str, nombre: str, apellido: str) -> Cliente:
        cliente = Cliente(dni=dni, nombre=nombre, apellido=apellido)
        self._clientes.agregar(cliente)
        return cliente

    def dar_de_baja_cliente(self, dni: str) -> None:
        cliente = self._clientes.obtener_por_dni(dni)
        if cliente is None:
            raise ClienteNoEncontradoError(
                f"No se encontró el cliente con DNI '{dni}'"
            )
        pendientes = [
            p for p in self._prestamos.obtener_por_cliente(dni)
            if not p.esta_devuelto()
        ]
        if pendientes:
            raise ClienteInactivoError(
                f"El cliente tiene {len(pendientes)} préstamo(s) sin devolver"
            )
        cliente.dar_de_baja()

    def obtener_clientes(self) -> List[Cliente]:
        return self._clientes.obtener_todos()

    def obtener_cliente(self, dni: str) -> Optional[Cliente]:
        return self._clientes.obtener_por_dni(dni)

    def obtener_clientes_activos(self) -> List[Cliente]:
        return self._clientes.obtener_activos()

    def obtener_prestamos_activos_de_cliente(self, dni: str) -> List[Prestamo]:
        cliente = self._clientes.obtener_por_dni(dni)
        if cliente is None:
            raise ClienteNoEncontradoError(
                f"No se encontró el cliente con DNI '{dni}'"
            )
        return [
            p for p in self._prestamos.obtener_por_cliente(dni)
            if not p.esta_devuelto()
        ]
