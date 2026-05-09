from typing import Optional, List

from ..models.cliente import Cliente
from ..exceptions import ClienteNoEncontradoError, ClienteYaExisteError


class ClienteRepository:
    def __init__(self):
        self._clientes: dict = {}

    def agregar(self, cliente: Cliente) -> None:
        if cliente.dni in self._clientes:
            raise ClienteYaExisteError(
                f"Ya existe un cliente con DNI '{cliente.dni}'"
            )
        self._clientes[cliente.dni] = cliente

    def obtener_por_dni(self, dni: str) -> Optional[Cliente]:
        return self._clientes.get(dni.strip())

    def obtener_todos(self) -> List[Cliente]:
        return list(self._clientes.values())

    def obtener_activos(self) -> List[Cliente]:
        return [c for c in self._clientes.values() if c.activo]

    def existe(self, dni: str) -> bool:
        return dni.strip() in self._clientes

    def cantidad(self) -> int:
        return len(self._clientes)
