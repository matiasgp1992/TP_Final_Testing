import pytest
from src.models.cliente import Cliente
from src.repositories.cliente_repository import ClienteRepository
from src.exceptions import ClienteYaExisteError


@pytest.fixture
def repo():
    return ClienteRepository()


@pytest.fixture
def cliente():
    return Cliente("12345678", "Juan", "Pérez")


@pytest.fixture
def cliente_alt():
    return Cliente("87654321", "María", "González")


class TestClienteRepositoryAgregar:
    def test_agregar_cliente_exitoso(self, repo, cliente):
        repo.agregar(cliente)
        assert repo.cantidad() == 1

    def test_agregar_dni_duplicado_lanza_error(self, repo, cliente):
        repo.agregar(cliente)
        with pytest.raises(ClienteYaExisteError):
            repo.agregar(Cliente("12345678", "Otro", "Nombre"))

    def test_agregar_varios_clientes(self, repo, cliente, cliente_alt):
        repo.agregar(cliente)
        repo.agregar(cliente_alt)
        assert repo.cantidad() == 2


class TestClienteRepositoryObtener:
    def test_obtener_por_dni_existente(self, repo, cliente):
        repo.agregar(cliente)
        resultado = repo.obtener_por_dni("12345678")
        assert resultado == cliente

    def test_obtener_por_dni_inexistente_retorna_none(self, repo):
        assert repo.obtener_por_dni("99999999") is None

    def test_obtener_por_dni_normaliza_espacios(self, repo, cliente):
        repo.agregar(cliente)
        assert repo.obtener_por_dni("  12345678  ") == cliente

    def test_obtener_todos_lista_vacia(self, repo):
        assert repo.obtener_todos() == []

    def test_obtener_activos_excluye_inactivos(self, repo, cliente, cliente_alt):
        repo.agregar(cliente)
        repo.agregar(cliente_alt)
        cliente.dar_de_baja()
        activos = repo.obtener_activos()
        assert cliente     not in activos
        assert cliente_alt in activos

    def test_obtener_activos_todos_activos(self, repo, cliente, cliente_alt):
        repo.agregar(cliente)
        repo.agregar(cliente_alt)
        assert len(repo.obtener_activos()) == 2

    def test_existe_cliente_registrado(self, repo, cliente):
        repo.agregar(cliente)
        assert repo.existe("12345678") is True

    def test_no_existe_cliente_no_registrado(self, repo):
        assert repo.existe("99999999") is False
