import pytest
from datetime import date, timedelta

from src.models.autor import Autor
from src.models.libro import Libro
from src.models.cliente import Cliente
from src.models.prestamo import Prestamo, EstadoPrestamo


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
def prestamo_activo(libro, cliente):
    hoy = date.today()
    return Prestamo(
        id="P0001",
        libro=libro,
        cliente=cliente,
        fecha_prestamo=hoy,
        fecha_devolucion_esperada=hoy + timedelta(days=14),
    )


@pytest.fixture
def prestamo_vencido(libro, cliente):
    ayer = date.today() - timedelta(days=1)
    hace_10 = date.today() - timedelta(days=10)
    return Prestamo(
        id="P0002",
        libro=libro,
        cliente=cliente,
        fecha_prestamo=hace_10,
        fecha_devolucion_esperada=ayer,
    )


@pytest.fixture
def prestamo_devuelto(libro, cliente):
    hoy = date.today()
    p = Prestamo(
        id="P0003",
        libro=libro,
        cliente=cliente,
        fecha_prestamo=hoy - timedelta(days=7),
        fecha_devolucion_esperada=hoy + timedelta(days=7),
    )
    p.fecha_devolucion_real = hoy
    return p


class TestPrestamoCreacion:
    def test_creacion_exitosa(self, libro, cliente):
        hoy = date.today()
        prestamo = Prestamo(
            id="P0001",
            libro=libro,
            cliente=cliente,
            fecha_prestamo=hoy,
            fecha_devolucion_esperada=hoy + timedelta(days=14),
        )
        assert prestamo.id == "P0001"
        assert prestamo.fecha_devolucion_real is None

    def test_fecha_devolucion_anterior_lanza_error(self, libro, cliente):
        hoy = date.today()
        with pytest.raises(ValueError):
            Prestamo(
                id="P0001",
                libro=libro,
                cliente=cliente,
                fecha_prestamo=hoy,
                fecha_devolucion_esperada=hoy,
            )

    def test_fecha_devolucion_igual_a_prestamo_lanza_error(self, libro, cliente):
        hoy = date.today()
        with pytest.raises(ValueError):
            Prestamo(
                id="P0001",
                libro=libro,
                cliente=cliente,
                fecha_prestamo=hoy,
                fecha_devolucion_esperada=hoy - timedelta(days=1),
            )


class TestPrestamoEstado:
    def test_prestamo_activo_no_esta_devuelto(self, prestamo_activo):
        assert prestamo_activo.esta_devuelto() is False

    def test_prestamo_activo_no_esta_vencido(self, prestamo_activo):
        assert prestamo_activo.esta_vencido() is False

    def test_prestamo_activo_estado_es_activo(self, prestamo_activo):
        assert prestamo_activo.estado() == EstadoPrestamo.ACTIVO

    def test_prestamo_vencido_no_esta_devuelto(self, prestamo_vencido):
        assert prestamo_vencido.esta_devuelto() is False

    def test_prestamo_vencido_esta_vencido(self, prestamo_vencido):
        assert prestamo_vencido.esta_vencido() is True

    def test_prestamo_vencido_estado_es_vencido(self, prestamo_vencido):
        assert prestamo_vencido.estado() == EstadoPrestamo.VENCIDO

    def test_prestamo_devuelto_esta_devuelto(self, prestamo_devuelto):
        assert prestamo_devuelto.esta_devuelto() is True

    def test_prestamo_devuelto_no_esta_vencido(self, prestamo_devuelto):
        assert prestamo_devuelto.esta_vencido() is False

    def test_prestamo_devuelto_estado_es_devuelto(self, prestamo_devuelto):
        assert prestamo_devuelto.estado() == EstadoPrestamo.DEVUELTO


class TestPrestamoDiasVencido:
    def test_activo_tiene_cero_dias_vencido(self, prestamo_activo):
        assert prestamo_activo.dias_vencido() == 0

    def test_vencido_tiene_dias_positivos(self, prestamo_vencido):
        assert prestamo_vencido.dias_vencido() >= 1

    def test_devuelto_tiene_cero_dias_vencido(self, prestamo_devuelto):
        assert prestamo_devuelto.dias_vencido() == 0
