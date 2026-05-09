import pytest
from datetime import date, timedelta

from src.models.autor import Autor
from src.models.libro import Libro
from src.models.cliente import Cliente
from src.models.prestamo import Prestamo
from src.repositories.autor_repository import AutorRepository
from src.repositories.libro_repository import LibroRepository
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.prestamo_repository import PrestamoRepository
from src.services.biblioteca_service import BibliotecaService
from src.services.prestamo_service import PrestamoService


# ── Fixtures de modelos ───────────────────────────────────────────────────────

@pytest.fixture
def autor():
    return Autor(nombre="Gabriel", apellido="García Márquez", nacionalidad="Colombiana")


@pytest.fixture
def autor_alt():
    return Autor(nombre="Jorge Luis", apellido="Borges", nacionalidad="Argentina")


@pytest.fixture
def libro(autor):
    return Libro(
        isbn="978-0-06-112008-4",
        titulo="Cien años de soledad",
        editorial="Sudamericana",
        autor=autor,
    )


@pytest.fixture
def libro_alt(autor_alt):
    return Libro(
        isbn="978-84-204-8645-5",
        titulo="Ficciones",
        editorial="Sur",
        autor=autor_alt,
    )


@pytest.fixture
def cliente():
    return Cliente(dni="12345678", nombre="Juan", apellido="Pérez")


@pytest.fixture
def cliente_alt():
    return Cliente(dni="87654321", nombre="María", apellido="González")


# ── Fixtures de repositorios ──────────────────────────────────────────────────

@pytest.fixture
def autor_repo():
    return AutorRepository()


@pytest.fixture
def libro_repo():
    return LibroRepository()


@pytest.fixture
def cliente_repo():
    return ClienteRepository()


@pytest.fixture
def prestamo_repo():
    return PrestamoRepository()


# ── Fixtures de servicios ─────────────────────────────────────────────────────

@pytest.fixture
def biblioteca_service(autor_repo, libro_repo, cliente_repo, prestamo_repo):
    return BibliotecaService(autor_repo, libro_repo, cliente_repo, prestamo_repo)


@pytest.fixture
def prestamo_service(libro_repo, cliente_repo, prestamo_repo):
    return PrestamoService(libro_repo, cliente_repo, prestamo_repo)


# ── Fixture de sistema completo (datos pre-cargados) ─────────────────────────

@pytest.fixture
def sistema_cargado(autor_repo, libro_repo, cliente_repo, prestamo_repo):
    """Sistema con un autor, libro, cliente y un préstamo activo ya registrados."""
    bsvc = BibliotecaService(autor_repo, libro_repo, cliente_repo, prestamo_repo)
    psvc = PrestamoService(libro_repo, cliente_repo, prestamo_repo)

    bsvc.agregar_autor("Gabriel", "García Márquez", "Colombiana")
    bsvc.agregar_libro(
        "978-0-06-112008-4", "Cien años de soledad", "Sudamericana",
        "Gabriel", "García Márquez",
    )
    bsvc.agregar_cliente("12345678", "Juan", "Pérez")
    prestamo = psvc.prestar_libro("978-0-06-112008-4", "12345678", dias=14)
    return bsvc, psvc, prestamo


@pytest.fixture
def prestamo_vencido(autor_repo, libro_repo, cliente_repo, prestamo_repo):
    """Préstamo con fecha de devolución ya pasada (vencido)."""
    autor   = Autor("Ana", "Karenina")
    libro   = Libro("ISBN-VENCIDO", "Libro vencido", "Editorial", autor)
    cliente = Cliente("11111111", "Pedro", "Vencido")

    autor_repo.agregar(autor)
    libro_repo.agregar(libro)
    cliente_repo.agregar(cliente)

    ayer = date.today() - timedelta(days=1)
    hace_10 = date.today() - timedelta(days=10)

    prestamo = Prestamo(
        id=prestamo_repo.nuevo_id(),
        libro=libro,
        cliente=cliente,
        fecha_prestamo=hace_10,
        fecha_devolucion_esperada=ayer,
    )
    libro.marcar_prestado()
    prestamo_repo.agregar(prestamo)
    return prestamo
