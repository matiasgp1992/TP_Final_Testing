from dataclasses import dataclass


@dataclass
class Cliente:
    dni: str
    nombre: str
    apellido: str
    activo: bool = True

    def __post_init__(self):
        if not self.dni or not self.dni.strip():
            raise ValueError("El DNI no puede estar vacío")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre no puede estar vacío")
        if not self.apellido or not self.apellido.strip():
            raise ValueError("El apellido no puede estar vacío")
        self.dni = self.dni.strip()
        self.nombre = self.nombre.strip()
        self.apellido = self.apellido.strip()

    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def dar_de_baja(self) -> None:
        self.activo = False

    def __eq__(self, other):
        if not isinstance(other, Cliente):
            return False
        return self.dni == other.dni

    def __hash__(self):
        return hash(self.dni)
