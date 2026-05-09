import pytest
from src.models.autor import Autor
from src.models.libro import Libro, EstadoLibro


@pytest.fixture
def autor():
    return Autor(nombre="Gabriel", apellido="García Márquez")


@pytest.fixture
def libro(autor):
    return Libro(
        isbn="978-0-06-112008-4",
        titulo="Cien años de soledad",
        editorial="Sudamericana",
        autor=autor,
    )


class TestLibroCreacion:
    def test_creacion_exitosa(self, autor):
        libro = Libro(
            isbn="123-456",
            titulo="Mi libro",
            editorial="Editorial X",
            autor=autor,
        )
        assert libro.isbn == "123-456"
        assert libro.titulo == "Mi libro"
        assert libro.editorial == "Editorial X"
        assert libro.autor == autor

    def test_estado_inicial_es_disponible(self, libro):
        assert libro.estado == EstadoLibro.DISPONIBLE

    def test_isbn_se_normaliza(self, autor):
        libro = Libro(isbn="  123  ", titulo="T", editorial="E", autor=autor)
        assert libro.isbn == "123"

    def test_isbn_vacio_lanza_error(self, autor):
        with pytest.raises(ValueError, match="ISBN"):
            Libro(isbn="", titulo="T", editorial="E", autor=autor)

    def test_titulo_vacio_lanza_error(self, autor):
        with pytest.raises(ValueError, match="título"):
            Libro(isbn="123", titulo="", editorial="E", autor=autor)

    def test_editorial_vacia_lanza_error(self, autor):
        with pytest.raises(ValueError, match="editorial"):
            Libro(isbn="123", titulo="T", editorial="", autor=autor)


class TestLibroEstado:
    def test_esta_disponible_por_defecto(self, libro):
        assert libro.esta_disponible() is True

    def test_marcar_prestado(self, libro):
        libro.marcar_prestado()
        assert libro.estado == EstadoLibro.PRESTADO
        assert libro.esta_disponible() is False

    def test_marcar_disponible_luego_de_prestado(self, libro):
        libro.marcar_prestado()
        libro.marcar_disponible()
        assert libro.esta_disponible() is True

    def test_doble_marcar_prestado_no_falla(self, libro):
        libro.marcar_prestado()
        libro.marcar_prestado()
        assert libro.estado == EstadoLibro.PRESTADO


class TestLibroIgualdad:
    def test_mismo_isbn_son_iguales(self, autor):
        l1 = Libro(isbn="123", titulo="A", editorial="E", autor=autor)
        l2 = Libro(isbn="123", titulo="B", editorial="E", autor=autor)
        assert l1 == l2

    def test_isbn_distinto_no_son_iguales(self, autor):
        l1 = Libro(isbn="123", titulo="A", editorial="E", autor=autor)
        l2 = Libro(isbn="456", titulo="A", editorial="E", autor=autor)
        assert l1 != l2

    def test_libro_no_es_igual_a_otro_tipo(self, libro):
        assert libro != "978-0-06-112008-4"
