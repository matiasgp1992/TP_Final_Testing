import pytest
from src.models.autor import Autor
from src.repositories.autor_repository import AutorRepository
from src.exceptions import AutorYaExisteError, AutorNoEncontradoError


@pytest.fixture
def repo():
    return AutorRepository()


@pytest.fixture
def autor():
    return Autor("Gabriel", "García Márquez", "Colombiana")


class TestAutorRepositoryAgregar:
    def test_agregar_autor_exitoso(self, repo, autor):
        repo.agregar(autor)
        assert repo.cantidad() == 1

    def test_agregar_autor_duplicado_lanza_error(self, repo, autor):
        repo.agregar(autor)
        with pytest.raises(AutorYaExisteError):
            repo.agregar(autor)

    def test_agregar_mismo_nombre_diferente_case_lanza_error(self, repo):
        repo.agregar(Autor("Gabriel", "García Márquez"))
        with pytest.raises(AutorYaExisteError):
            repo.agregar(Autor("gabriel", "garcía márquez"))

    def test_agregar_varios_autores(self, repo):
        repo.agregar(Autor("Gabriel", "García Márquez"))
        repo.agregar(Autor("Jorge",   "Borges"))
        assert repo.cantidad() == 2


class TestAutorRepositoryBuscar:
    def test_buscar_autor_existente(self, repo, autor):
        repo.agregar(autor)
        resultado = repo.buscar("Gabriel", "García Márquez")
        assert resultado == autor

    def test_buscar_autor_inexistente_retorna_none(self, repo):
        resultado = repo.buscar("Nadie", "Nunca")
        assert resultado is None

    def test_existe_autor_registrado(self, repo, autor):
        repo.agregar(autor)
        assert repo.existe("Gabriel", "García Márquez") is True

    def test_no_existe_autor_no_registrado(self, repo):
        assert repo.existe("Nadie", "Nunca") is False


class TestAutorRepositoryObtenerTodos:
    def test_obtener_todos_lista_vacia(self, repo):
        assert repo.obtener_todos() == []

    def test_obtener_todos_retorna_autores(self, repo, autor):
        repo.agregar(autor)
        todos = repo.obtener_todos()
        assert len(todos) == 1
        assert autor in todos

    def test_obtener_todos_independiente_de_orden(self, repo):
        a1 = Autor("Ana",   "García")
        a2 = Autor("Bruno", "López")
        repo.agregar(a1)
        repo.agregar(a2)
        todos = repo.obtener_todos()
        assert a1 in todos
        assert a2 in todos


class TestAutorRepositoryEliminar:
    def test_eliminar_autor_existente(self, repo, autor):
        repo.agregar(autor)
        repo.eliminar("Gabriel", "García Márquez")
        assert repo.cantidad() == 0

    def test_eliminar_autor_inexistente_lanza_error(self, repo):
        with pytest.raises(AutorNoEncontradoError):
            repo.eliminar("Nadie", "Nunca")
