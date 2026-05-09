import pytest
from datetime import date, timedelta

from src.exceptions import (
    LibroNoEncontradoError,
    LibroNoDisponibleError,
    ClienteNoEncontradoError,
    ClienteInactivoError,
    PrestamoNoEncontradoError,
    PrestamoYaDevueltoError,
)
from src.models.libro import EstadoLibro
from src.models.prestamo import EstadoPrestamo


class TestPrestamoServicePrestar:
    def test_prestar_libro_exitoso(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        assert prestamo.id is not None
        assert prestamo.libro.estado == EstadoLibro.PRESTADO

    def test_prestar_cambia_estado_libro(self, sistema_cargado):
        _, _, prestamo = sistema_cargado
        assert prestamo.libro.esta_disponible() is False

    def test_prestar_establece_fecha_correcta(self, sistema_cargado):
        _, _, prestamo = sistema_cargado
        assert prestamo.fecha_prestamo == date.today()
        assert prestamo.fecha_devolucion_esperada == date.today() + timedelta(days=14)

    def test_prestar_con_dias_personalizados(self, biblioteca_service, prestamo_service):
        biblioteca_service.agregar_autor("Ana", "Karenina")
        biblioteca_service.agregar_libro("ISBN-K", "Libro K", "Ed", "Ana", "Karenina")
        biblioteca_service.agregar_cliente("99999999", "Test", "User")
        prestamo = prestamo_service.prestar_libro("ISBN-K", "99999999", dias=30)
        assert prestamo.fecha_devolucion_esperada == date.today() + timedelta(days=30)

    def test_prestar_libro_inexistente_lanza_error(self, prestamo_service):
        with pytest.raises(LibroNoEncontradoError):
            prestamo_service.prestar_libro("ISBN-NO-EXISTE", "12345678")

    def test_prestar_libro_no_disponible_lanza_error(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        with pytest.raises(LibroNoDisponibleError):
            psvc.prestar_libro(prestamo.libro.isbn, prestamo.cliente.dni)

    def test_prestar_a_cliente_inexistente_lanza_error(self, biblioteca_service, prestamo_service):
        biblioteca_service.agregar_autor("Test", "Autor")
        biblioteca_service.agregar_libro("ISBN-T", "Test", "Ed", "Test", "Autor")
        with pytest.raises(ClienteNoEncontradoError):
            prestamo_service.prestar_libro("ISBN-T", "CLIENTE-NO-EXISTE")

    def test_prestar_a_cliente_inactivo_lanza_error(self, biblioteca_service, prestamo_service):
        biblioteca_service.agregar_autor("Test", "Autor")
        biblioteca_service.agregar_libro("ISBN-T2", "Test2", "Ed", "Test", "Autor")
        biblioteca_service.agregar_cliente("55555555", "Inactivo", "Cliente")
        biblioteca_service.dar_de_baja_cliente("55555555")
        with pytest.raises(ClienteInactivoError):
            prestamo_service.prestar_libro("ISBN-T2", "55555555")


class TestPrestamoServiceDevolver:
    def test_devolver_libro_exitoso(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        devuelto = psvc.devolver_libro(prestamo.id)
        assert devuelto.esta_devuelto() is True
        assert devuelto.fecha_devolucion_real == date.today()

    def test_devolver_restaura_estado_libro(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        psvc.devolver_libro(prestamo.id)
        assert prestamo.libro.esta_disponible() is True

    def test_devolver_prestamo_inexistente_lanza_error(self, prestamo_service):
        with pytest.raises(PrestamoNoEncontradoError):
            prestamo_service.devolver_libro("P9999")

    def test_devolver_prestamo_ya_devuelto_lanza_error(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        psvc.devolver_libro(prestamo.id)
        with pytest.raises(PrestamoYaDevueltoError):
            psvc.devolver_libro(prestamo.id)


class TestPrestamoServiceConsultas:
    def test_obtener_prestamos_activos(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        activos = psvc.obtener_prestamos_activos()
        assert prestamo in activos

    def test_devuelto_no_aparece_en_activos(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        psvc.devolver_libro(prestamo.id)
        activos = psvc.obtener_prestamos_activos()
        assert prestamo not in activos

    def test_obtener_vencidos(self, prestamo_service, prestamo_vencido):
        vencidos = prestamo_service.obtener_vencidos()
        assert prestamo_vencido in vencidos

    def test_vencido_no_aparece_tras_devolucion(self, prestamo_service, prestamo_vencido):
        prestamo_service.devolver_libro(prestamo_vencido.id)
        assert prestamo_service.obtener_vencidos() == []

    def test_obtener_prestamos_de_cliente(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        dni = prestamo.cliente.dni
        resultados = psvc.obtener_prestamos_de_cliente(dni)
        assert prestamo in resultados

    def test_prestamos_de_cliente_sin_historial(self, prestamo_service):
        assert prestamo_service.obtener_prestamos_de_cliente("99999999") == []

    def test_estado_prestamo_activo(self, sistema_cargado):
        _, _, prestamo = sistema_cargado
        assert prestamo.estado() == EstadoPrestamo.ACTIVO

    def test_estado_prestamo_vencido(self, prestamo_service, prestamo_vencido):
        assert prestamo_vencido.estado() == EstadoPrestamo.VENCIDO

    def test_estado_prestamo_devuelto(self, sistema_cargado):
        bsvc, psvc, prestamo = sistema_cargado
        psvc.devolver_libro(prestamo.id)
        assert prestamo.estado() == EstadoPrestamo.DEVUELTO
