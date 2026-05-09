import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ...services.prestamo_service import PrestamoService
from ...exceptions import PrestamoNoEncontradoError, PrestamoYaDevueltoError


class VencidosFrame(ttk.Frame):
    def __init__(
        self, parent,
        prestamo_svc: PrestamoService,
        on_devolucion: Callable,
    ):
        super().__init__(parent)
        self._psvc = prestamo_svc
        self._on_devolucion = on_devolucion
        self._construir_ui()
        self.actualizar()

    def _construir_ui(self):
        # Panel de alerta
        self._panel_alerta = tk.Frame(self, bg="#fff5f5", pady=10)
        self._panel_alerta.pack(fill="x", padx=12, pady=(12, 0))

        self._lbl_alerta = tk.Label(
            self._panel_alerta,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg="#fff5f5",
            fg="#c53030",
        )
        self._lbl_alerta.pack(side="left", padx=12)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=12, pady=(10, 0))

        ttk.Button(
            toolbar, text="Registrar Devolución",
            command=self._devolver,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            toolbar, text="Actualizar",
            command=self.actualizar,
        ).pack(side="left")

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill="both", expand=True, padx=12, pady=10)

        cols = ("id", "libro", "cliente", "prestado", "vencio", "dias_vencido")
        self._tree = ttk.Treeview(
            frame_tree, columns=cols, show="headings", selectmode="browse"
        )
        titulos = {
            "id":          "ID",
            "libro":       "Libro",
            "cliente":     "Cliente",
            "prestado":    "Fecha Préstamo",
            "vencio":      "Venció el",
            "dias_vencido": "Días vencido",
        }
        anchos = {
            "id": 70, "libro": 250, "cliente": 200,
            "prestado": 120, "vencio": 120, "dias_vencido": 110,
        }
        for col in cols:
            self._tree.heading(col, text=titulos[col])
            self._tree.column(
                col, width=anchos[col],
                anchor="center" if col != "libro" and col != "cliente" else "w",
            )

        self._tree.tag_configure(
            "vencido", background="#fff5f5", foreground="#c53030"
        )

        sb = ttk.Scrollbar(frame_tree, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._lbl_status = ttk.Label(self, text="", foreground="#718096")
        self._lbl_status.pack(anchor="w", padx=12, pady=(0, 6))

    def actualizar(self, *_):
        self._tree.delete(*self._tree.get_children())
        vencidos = self._psvc.obtener_vencidos()

        for p in vencidos:
            self._tree.insert(
                "", "end", iid=p.id,
                values=(
                    p.id,
                    p.libro.titulo,
                    p.cliente.nombre_completo(),
                    p.fecha_prestamo.strftime("%d/%m/%Y"),
                    p.fecha_devolucion_esperada.strftime("%d/%m/%Y"),
                    f"{p.dias_vencido()} día(s)",
                ),
                tags=("vencido",),
            )

        n = len(vencidos)
        if n == 0:
            self._lbl_alerta.config(text="Sin préstamos vencidos.")
            self._panel_alerta.config(bg="#f0fff4")
            self._lbl_alerta.config(bg="#f0fff4", fg="#276749")
        else:
            self._lbl_alerta.config(
                text=f"¡Atención! Hay {n} préstamo(s) vencido(s) pendiente(s) de devolución."
            )
            self._panel_alerta.config(bg="#fff5f5")
            self._lbl_alerta.config(bg="#fff5f5", fg="#c53030")

        self._lbl_status.config(text=f"{n} préstamo(s) vencido(s)")

    def _devolver(self):
        sel = self._tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione un préstamo de la lista.")
            return
        valores = self._tree.item(sel, "values")
        prestamo_id, titulo = valores[0], valores[1]
        if not messagebox.askyesno(
            "Confirmar devolución",
            f"¿Registrar devolución del libro '{titulo}'?",
        ):
            return
        try:
            self._psvc.devolver_libro(prestamo_id)
            self.actualizar()
            self._on_devolucion()
            messagebox.showinfo("Éxito", "Devolución registrada correctamente.")
        except (PrestamoNoEncontradoError, PrestamoYaDevueltoError) as e:
            messagebox.showerror("Error", str(e))
