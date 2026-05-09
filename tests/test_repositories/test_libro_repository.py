import pytest
from src.models.autor import Autor
from src.models.libro import Libro
from src.repositories.libro_repository import LibroRepository
from src.exceptions import LibroYaExisteError, LibroNoEncontradoError


@pytest.fixture
def repo():
    return LibroRepository()


@pytest.fixture
def autor():
    return Autor("Gabriel", "García Márquez")


@pytest.fixture
def libro(autor):
    return Libro("ISBN-001", "Cien años de soledad", "Sudamericana", autor)


@pytest.fixture
def libro_alt(autor):
    return Libro("ISBN-002", "El amor en los tiempos del cólera", "Oveja Negra", autor)


class TestLibroRepositoryAgregar:
    def test_agregar_libro_exitoso(self, repo, libro):
        repo.agregar(libro)
        assert repo.cantidad() == 1

    def test_agregar_isbn_duplicado_lanza_error(self, repo, libro):
        repo.agregar(libro)
        with pytest.raises(LibroYaExisteError):
            repo.agregar(libro)

    def test_agregar_varios_libros(self, repo, libro, libro_alt):
        repo.agregar(libro)
        repo.agregar(libro_alt)
        assert repo.cantidad() == 2


class TestLibroRepositoryObtener:
    def test_obtener_por_isbn_existente(self, repo, libro):
        repo.agregar(libro)
        resultado = repo.obtener_por_isbn("ISBN-001")
        assert resultado == libro

    def test_obtener_por_isbn_inexistente_retorna_none(self, repo):
        assert repo.obtener_por_isbn("NO-EXISTE") is None

    def test_obtener_por_isbn_normaliza_espacios(self, repo, libro):
        repo.agregar(libro)
        resultado = repo.obtener_por_isbn("  ISBN-001  ")
        assert resultado == libro

    def test_obtener_todos_lista_vacia(self, repo):
        assert repo.obtener_todos() == []

    def test_obtener_todos_retorna_libros(self, repo, libro, libro_alt):
        repo.agregar(libro)
        repo.agregar(libro_alt)
        todos = repo.obtener_todos()
        assert len(todos) == 2

    def test_obtener_disponibles_solo_disponibles(self, repo, libro, libro_alt):
        repo.agregar(libro)
        repo.agregar(libro_alt)
        libro.marcar_prestado()
        disponibles = repo.obtener_disponibles()
        assert libro     not in disponibles
        assert libro_alt in disponibles

    def test_existe_isbn_registrado(self, repo, libro):
        repo.agregar(libro)
        assert repo.existe("ISBN-001") is True

    def test_no_existe_isbn_no_registrado(self, repo):
        assert repo.existe("NO-EXISTE") is False


class TestLibroRepositoryEliminar:
    def test_eliminar_libro_existente(self, repo, libro):
        repo.agregar(libro)
        repo.eliminar("ISBN-001")
        assert repo.cantidad() == 0

    def test_eliminar_libro_inexistente_lanza_error(self, repo):
        with pytest.raises(LibroNoEncontradoError):
            repo.eliminar("NO-EXISTE")

    def test_eliminar_no_afecta_otros_libros(self, repo, libro, libro_alt):
        repo.agregar(libro)
        repo.agregar(libro_alt)
        repo.eliminar("ISBN-001")
        assert repo.existe("ISBN-002") is True
        assert repo.cantidad() == 1
