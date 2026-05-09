import pytest
from src.models.cliente import Cliente


class TestClienteCreacion:
    def test_creacion_exitosa(self):
        cliente = Cliente(dni="12345678", nombre="Juan", apellido="Pérez")
        assert cliente.dni == "12345678"
        assert cliente.nombre == "Juan"
        assert cliente.apellido == "Pérez"
        assert cliente.activo is True

    def test_datos_se_normalizan(self):
        cliente = Cliente(dni="  12345678  ", nombre="  Juan  ", apellido="  Pérez  ")
        assert cliente.dni == "12345678"
        assert cliente.nombre == "Juan"
        assert cliente.apellido == "Pérez"

    def test_dni_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="DNI"):
            Cliente(dni="", nombre="Juan", apellido="Pérez")

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="nombre"):
            Cliente(dni="123", nombre="", apellido="Pérez")

    def test_apellido_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="apellido"):
            Cliente(dni="123", nombre="Juan", apellido="")


class TestClienteNombreCompleto:
    def test_nombre_completo(self):
        cliente = Cliente(dni="123", nombre="Juan", apellido="Pérez")
        assert cliente.nombre_completo() == "Juan Pérez"


class TestClienteDarDeBaja:
    def test_dar_de_baja_cambia_estado(self):
        cliente = Cliente(dni="123", nombre="Juan", apellido="Pérez")
        cliente.dar_de_baja()
        assert cliente.activo is False

    def test_dar_de_baja_dos_veces_no_falla(self):
        cliente = Cliente(dni="123", nombre="Juan", apellido="Pérez")
        cliente.dar_de_baja()
        cliente.dar_de_baja()
        assert cliente.activo is False


class TestClienteIgualdad:
    def test_mismo_dni_son_iguales(self):
        c1 = Cliente(dni="123", nombre="Juan", apellido="Pérez")
        c2 = Cliente(dni="123", nombre="María", apellido="López")
        assert c1 == c2

    def test_dni_distinto_no_son_iguales(self):
        c1 = Cliente(dni="123", nombre="Juan", apellido="Pérez")
        c2 = Cliente(dni="456", nombre="Juan", apellido="Pérez")
        assert c1 != c2

    def test_cliente_no_es_igual_a_otro_tipo(self):
        cliente = Cliente(dni="123", nombre="Juan", apellido="Pérez")
        assert cliente != "123"
