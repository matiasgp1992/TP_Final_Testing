import pytest
from src.exceptions import (
    AutorYaExisteError,
    AutorNoEncontradoError,
    LibroYaExisteError,
    LibroNoEncontradoError,
    LibroPrestadoError,
    ClienteYaExisteError,
    ClienteNoEncontradoError,
    ClienteInactivoError,
)
from src.models.libro import EstadoLibro


class TestBibliotecaServiceAutores:
    def test_agregar_autor_exitoso(self, biblioteca_service):
        autor = biblioteca_service.agregar_autor("Gabriel", "García Márquez", "Colombiana")
        assert autor.nombre == "Gabriel"
        assert autor.apellido == "García Márquez"

    def test_agregar_autor_duplicado_lanza_error(self, biblioteca_service):
        biblioteca_service.agregar_autor("Gabriel", "García Márquez")
        with pytest.raises(AutorYaExisteError):
            biblioteca_service.agregar_autor("Gabriel", "García Márquez")

    def test_obtener_autores_vacio(self, biblioteca_service):
        assert biblioteca_service.obtener_autores() == []

    def test_obtener_autores_retorna_todos(self, biblioteca_service):
        biblioteca_service.agregar_autor("Gabriel", "García Márquez")
        biblioteca_service.agregar_autor("Jorge",   "Borges")
        assert len(biblioteca_service.obtener_autores()) == 2

    def test_buscar_autor_existente(self, biblioteca_service):
        biblioteca_service.agregar_autor("Gabriel", "García Márquez")
        resultado = biblioteca_service.buscar_autor("Gabriel", "García Márquez")
        assert resultado is not None
        assert resultado.nombre == "Gabriel"

    def test_buscar_autor_inexistente_retorna_none(self, biblioteca_service):
        assert biblioteca_service.buscar_autor("Nadie", "Nunca") is None


class TestBibliotecaServiceLibros:
    def test_agregar_libro_exitoso(self, biblioteca_service):
        biblioteca_service.agregar_autor("Gabriel", "García Márquez")
        libro = biblioteca_service.agregar_libro(
            "ISBN-001", "Cien años", "Sudamericana", "Gabriel", "García Márquez"
        )
        assert libro.isbn == "ISBN-001"
        assert libro.titulo == "Cien años"

    def test_agregar_libro_sin_autor_lanza_error(self, biblioteca_service):
        with pytest.raises(AutorNoEncontradoError):
            biblioteca_service.agregar_libro(
                "ISBN-001", "Cien años", "Sudamericana", "Nadie", "Nunca"
            )

    def test_agregar_libro_isbn_duplicado_lanza_error(self, biblioteca_service):
        biblioteca_service.agregar_autor("Gabriel", "García Márquez")
        biblioteca_service.agregar_libro(
            "ISBN-001", "Cien años", "Sudamericana", "Gabriel", "García Márquez"
        )
        with pytest.raises(LibroYaExisteError):
            biblioteca_service.agregar_libro(
                "ISBN-001", "Otro título", "Otra", "Gabriel", "García Márquez"
            )

    def test_obtener_libros_vacio(self, biblioteca_service):
        assert biblioteca_service.obtener_libros() == []

    def test_dar_de_baja_libro_disponible(self, biblioteca_service):
        biblioteca_service.agregar_autor("Gabriel", "García Márquez")
        biblioteca_service.agregar_libro(
            "ISBN-001", "Cien años", "Sudamericana", "Gabriel", "García Márquez"
        )
        biblioteca_service.dar_de_baja_libro("ISBN-001")
        assert biblioteca_service.obtener_libro("ISBN-001") is None

    def test_dar_de_baja_libro_prestado_lanza_error(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        with pytest.raises(LibroPrestadoError):
            bsvc.dar_de_baja_libro(prestamo.libro.isbn)

    def test_dar_de_baja_libro_inexistente_lanza_error(self, biblioteca_service):
        with pytest.raises(LibroNoEncontradoError):
            biblioteca_service.dar_de_baja_libro("NO-EXISTE")

    def test_obtener_libros_disponibles(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        bsvc.agregar_autor("Jorge", "Borges")
        bsvc.agregar_libro("ISBN-002", "Ficciones", "Sur", "Jorge", "Borges")
        disponibles = bsvc.obtener_libros_disponibles()
        assert any(l.isbn == "ISBN-002" for l in disponibles)
        assert all(l.esta_disponible() for l in disponibles)


class TestBibliotecaServiceClientes:
    def test_agregar_cliente_exitoso(self, biblioteca_service):
        cliente = biblioteca_service.agregar_cliente("12345678", "Juan", "Pérez")
        assert cliente.dni == "12345678"
        assert cliente.activo is True

    def test_agregar_cliente_dni_duplicado_lanza_error(self, biblioteca_service):
        biblioteca_service.agregar_cliente("12345678", "Juan", "Pérez")
        with pytest.raises(ClienteYaExisteError):
            biblioteca_service.agregar_cliente("12345678", "Otro", "Nombre")

    def test_obtener_clientes_vacio(self, biblioteca_service):
        assert biblioteca_service.obtener_clientes() == []

    def test_obtener_clientes_activos(self, biblioteca_service):
        biblioteca_service.agregar_cliente("11111111", "Juan",  "Pérez")
        biblioteca_service.agregar_cliente("22222222", "María", "González")
        biblioteca_service.dar_de_baja_cliente("11111111")
        activos = biblioteca_service.obtener_clientes_activos()
        assert len(activos) == 1
        assert activos[0].dni == "22222222"

    def test_dar_de_baja_cliente_sin_prestamos(self, biblioteca_service):
        biblioteca_service.agregar_cliente("12345678", "Juan", "Pérez")
        biblioteca_service.dar_de_baja_cliente("12345678")
        cliente = biblioteca_service.obtener_cliente("12345678")
        assert cliente.activo is False

    def test_dar_de_baja_cliente_con_prestamos_lanza_error(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        with pytest.raises(ClienteInactivoError):
            bsvc.dar_de_baja_cliente(prestamo.cliente.dni)

    def test_dar_de_baja_cliente_inexistente_lanza_error(self, biblioteca_service):
        with pytest.raises(ClienteNoEncontradoError):
            biblioteca_service.dar_de_baja_cliente("99999999")

    def test_obtener_prestamos_activos_de_cliente(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        activos = bsvc.obtener_prestamos_activos_de_cliente(prestamo.cliente.dni)
        assert len(activos) == 1
        assert activos[0].id == prestamo.id

    def test_obtener_prestamos_activos_cliente_inexistente_lanza_error(self, biblioteca_service):
        with pytest.raises(ClienteNoEncontradoError):
            biblioteca_service.obtener_prestamos_activos_de_cliente("99999999")
