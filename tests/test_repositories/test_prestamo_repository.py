import pytest
from datetime import date, timedelta

from src.models.autor import Autor
from src.models.libro import Libro
from src.models.cliente import Cliente
from src.models.prestamo import Prestamo
from src.repositories.prestamo_repository import PrestamoRepository


@pytest.fixture
def repo():
    return PrestamoRepository()


@pytest.fixture
def autor():
    return Autor("Gabriel", "García Márquez")


@pytest.fixture
def libro(autor):
    return Libro("ISBN-001", "Cien años", "Sudamericana", autor)


@pytest.fixture
def cliente():
    return Cliente("12345678", "Juan", "Pérez")


@pytest.fixture
def prestamo_activo(repo, libro, cliente):
    hoy = date.today()
    p = Prestamo(
        id=repo.nuevo_id(),
        libro=libro,
        cliente=cliente,
        fecha_prestamo=hoy,
        fecha_devolucion_esperada=hoy + timedelta(days=14),
    )
    repo.agregar(p)
    return p


@pytest.fixture
def prestamo_vencido(repo, autor, cliente):
    libro2 = Libro("ISBN-002", "Otro libro", "Editorial", autor)
    ayer   = date.today() - timedelta(days=1)
    hace10 = date.today() - timedelta(days=10)
    p = Prestamo(
        id=repo.nuevo_id(),
        libro=libro2,
        cliente=cliente,
        fecha_prestamo=hace10,
        fecha_devolucion_esperada=ayer,
    )
    repo.agregar(p)
    return p


class TestPrestamoRepositoryId:
    def test_ids_son_unicos_y_secuenciales(self, repo):
        id1 = repo.nuevo_id()
        id2 = repo.nuevo_id()
        id3 = repo.nuevo_id()
        assert id1 != id2
        assert id2 != id3

    def test_formato_de_id(self, repo):
        id1 = repo.nuevo_id()
        assert id1.startswith("P")


class TestPrestamoRepositoryAgregar:
    def test_agregar_prestamo_exitoso(self, repo, prestamo_activo):
        assert repo.cantidad() == 1

    def test_obtener_por_id_existente(self, repo, prestamo_activo):
        resultado = repo.obtener_por_id(prestamo_activo.id)
        assert resultado == prestamo_activo

    def test_obtener_por_id_inexistente_retorna_none(self, repo):
        assert repo.obtener_por_id("P9999") is None


class TestPrestamoRepositoryFiltros:
    def test_obtener_todos(self, repo, prestamo_activo, prestamo_vencido):
        todos = repo.obtener_todos()
        assert len(todos) == 2

    def test_obtener_por_cliente(self, repo, prestamo_activo, cliente):
        resultados = repo.obtener_por_cliente(cliente.dni)
        assert prestamo_activo in resultados

    def test_obtener_por_cliente_sin_prestamos(self, repo):
        assert repo.obtener_por_cliente("99999999") == []

    def test_obtener_activos_excluye_devueltos(self, repo, prestamo_activo):
        prestamo_activo.fecha_devolucion_real = date.today()
        activos = repo.obtener_activos()
        assert prestamo_activo not in activos

    def test_obtener_activos_incluye_vencidos_no_devueltos(self, repo, prestamo_vencido):
        activos = repo.obtener_activos()
        assert prestamo_vencido in activos

    def test_obtener_vencidos(self, repo, prestamo_activo, prestamo_vencido):
        vencidos = repo.obtener_vencidos()
        assert prestamo_vencido in vencidos
        assert prestamo_activo not in vencidos

    def test_obtener_vencidos_no_incluye_devueltos(self, repo, prestamo_vencido):
        prestamo_vencido.fecha_devolucion_real = date.today()
        assert repo.obtener_vencidos() == []
