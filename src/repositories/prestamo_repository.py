from typing import Optional, List

from ..models.prestamo import Prestamo
from ..exceptions import PrestamoNoEncontradoError


class PrestamoRepository:
    def __init__(self):
        self._prestamos: dict = {}
        self._contador: int = 0

    def _generar_id(self) -> str:
        self._contador += 1
        return f"P{self._contador:04d}"

    def nuevo_id(self) -> str:
        return self._generar_id()

    def agregar(self, prestamo: Prestamo) -> None:
        self._prestamos[prestamo.id] = prestamo

    def obtener_por_id(self, id: str) -> Optional[Prestamo]:
        return self._prestamos.get(id)

    def obtener_todos(self) -> List[Prestamo]:
        return list(self._prestamos.values())

    def obtener_por_cliente(self, dni: str) -> List[Prestamo]:
        return [p for p in self._prestamos.values() if p.cliente.dni == dni]

    def obtener_activos(self) -> List[Prestamo]:
        return [p for p in self._prestamos.values() if not p.esta_devuelto()]

    def obtener_vencidos(self) -> List[Prestamo]:
        return [p for p in self._prestamos.values() if p.esta_vencido()]

    def cantidad(self) -> int:
        return len(self._prestamos)
