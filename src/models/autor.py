from dataclasses import dataclass


@dataclass
class Autor:
    nombre: str
    apellido: str
    nacionalidad: str = ""

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del autor no puede estar vacío")
        if not self.apellido or not self.apellido.strip():
            raise ValueError("El apellido del autor no puede estar vacío")
        self.nombre = self.nombre.strip()
        self.apellido = self.apellido.strip()
        self.nacionalidad = self.nacionalidad.strip()

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def __eq__(self, other):
        if not isinstance(other, Autor):
            return False
        return (self.nombre.lower() == other.nombre.lower() and
                self.apellido.lower() == other.apellido.lower())

    def __hash__(self):
        return hash((self.nombre.lower(), self.apellido.lower()))
