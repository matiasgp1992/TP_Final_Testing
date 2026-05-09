import pytest
from src.models.autor import Autor


class TestAutorCreacion:
    def test_creacion_exitosa(self):
        autor = Autor(nombre="Gabriel", apellido="García Márquez", nacionalidad="Colombiana")
        assert autor.nombre == "Gabriel"
        assert autor.apellido == "García Márquez"
        assert autor.nacionalidad == "Colombiana"

    def test_creacion_sin_nacionalidad(self):
        autor = Autor(nombre="Jorge", apellido="Borges")
        assert autor.nacionalidad == ""

    def test_nombre_se_normaliza(self):
        autor = Autor(nombre="  Ana  ", apellido="  Karenina  ")
        assert autor.nombre == "Ana"
        assert autor.apellido == "Karenina"

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="nombre"):
            Autor(nombre="", apellido="Pérez")

    def test_nombre_solo_espacios_lanza_error(self):
        with pytest.raises(ValueError, match="nombre"):
            Autor(nombre="   ", apellido="Pérez")

    def test_apellido_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="apellido"):
            Autor(nombre="Juan", apellido="")


class TestAutorNombreCompleto:
    def test_nombre_completo(self):
        autor = Autor(nombre="Gabriel", apellido="García Márquez")
        assert autor.nombre_completo() == "Gabriel García Márquez"

    def test_nombre_completo_un_nombre(self):
        autor = Autor(nombre="Homero", apellido="Simpson")
        assert autor.nombre_completo() == "Homero Simpson"


class TestAutorIgualdad:
    def test_mismos_autores_son_iguales(self):
        a1 = Autor(nombre="Gabriel", apellido="García Márquez")
        a2 = Autor(nombre="Gabriel", apellido="García Márquez")
        assert a1 == a2

    def test_autores_distintos_no_son_iguales(self):
        a1 = Autor(nombre="Gabriel", apellido="García Márquez")
        a2 = Autor(nombre="Jorge",   apellido="Borges")
        assert a1 != a2

    def test_igualdad_case_insensitive(self):
        a1 = Autor(nombre="gabriel", apellido="garcía márquez")
        a2 = Autor(nombre="Gabriel", apellido="García Márquez")
        assert a1 == a2

    def test_autor_no_es_igual_a_otro_tipo(self):
        autor = Autor(nombre="Gabriel", apellido="García Márquez")
        assert autor != "Gabriel García Márquez"

    def test_autores_hashables_en_conjunto(self):
        a1 = Autor(nombre="Gabriel", apellido="García Márquez")
        a2 = Autor(nombre="Gabriel", apellido="García Márquez")
        conjunto = {a1, a2}
        assert len(conjunto) == 1
