import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from ...services.biblioteca_service import BibliotecaService
from ...services.prestamo_service import PrestamoService
from ...exceptions import (
    LibroNoDisponibleError,
    LibroNoEncontradoError,
    ClienteNoEncontradoError,
    ClienteInactivoError,
    PrestamoNoEncontradoError,
    PrestamoYaDevueltoError,
)


class PrestamosFrame(ttk.Frame):
    def __init__(
        self, parent,
        biblioteca_svc: BibliotecaService,
        prestamo_svc: PrestamoService,
        on_update: Callable,
    ):
        super().__init__(parent)
        self._bsvc = biblioteca_svc
        self._psvc = prestamo_svc
        self._on_update = on_update
        self._construir_ui()
        self.actualizar()

    def _construir_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(toolbar, text="+ Nuevo Préstamo",    command=self._nuevo_prestamo).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(toolbar, text="Registrar Devolución", command=self._devolver).pack(
            side="left", padx=(0, 16)
        )

        ttk.Label(toolbar, text="Buscar:").pack(side="left", padx=(0, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *_: self.actualizar())
        ttk.Entry(toolbar, textvariable=self._var_busqueda, width=22).pack(side="left")

        ttk.Label(toolbar, text="Estado:").pack(side="left", padx=(16, 4))
        self._var_filtro = tk.StringVar(value="Todos")
        cb = ttk.Combobox(
            toolbar, textvariable=self._var_filtro,
            values=["Todos", "Activo", "Vencido", "Devuelto"],
            state="readonly", width=10,
        )
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda _: self.actualizar())

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill="both", expand=True, padx=12, pady=10)

        cols = ("id", "libro", "cliente", "prestado", "vence", "devuelto", "estado")
        self._tree = ttk.Treeview(
            frame_tree, columns=cols, show="headings", selectmode="browse"
        )
        anchos = {"id": 70, "libro": 220, "cliente": 180,
                  "prestado": 110, "vence": 110, "devuelto": 110, "estado": 90}
        titulos = {"id": "ID", "libro": "Libro", "cliente": "Cliente",
                   "prestado": "Préstamo", "vence": "Vence",
                   "devuelto": "Devuelto", "estado": "Estado"}
        for col in cols:
            self._tree.heading(col, text=titulos[col])
            self._tree.column(
                col, width=anchos[col],
                anchor="center" if col in ("id", "prestado", "vence", "devuelto", "estado") else "w",
            )

        self._tree.tag_configure("vencido",   background="#fff5f5", foreground="#c53030")
        self._tree.tag_configure("devuelto",  background="#f0fff4", foreground="#276749")
        self._tree.tag_configure("activo",    foreground="#2d3748")

        sb = ttk.Scrollbar(frame_tree, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._lbl_status = ttk.Label(self, text="", foreground="#718096")
        self._lbl_status.pack(anchor="w", padx=12, pady=(0, 6))

    def actualizar(self, *_):
        busqueda = self._var_busqueda.get().lower()
        filtro   = self._var_filtro.get()

        self._tree.delete(*self._tree.get_children())
        prestamos = self._psvc.obtener_prestamos()

        if filtro == "Activo":
            prestamos = [p for p in prestamos if p.estado().value == "Activo"]
        elif filtro == "Vencido":
            prestamos = [p for p in prestamos if p.esta_vencido()]
        elif filtro == "Devuelto":
            prestamos = [p for p in prestamos if p.esta_devuelto()]

        if busqueda:
            prestamos = [
                p for p in prestamos
                if busqueda in p.libro.titulo.lower()
                or busqueda in p.cliente.nombre_completo().lower()
                or busqueda in p.id.lower()
            ]

        for p in prestamos:
            estado = p.estado()
            tag = estado.value.lower()
            devuelto_str = (
                p.fecha_devolucion_real.strftime("%d/%m/%Y")
                if p.fecha_devolucion_real else "—"
            )
            self._tree.insert(
                "", "end", iid=p.id,
                values=(
                    p.id,
                    p.libro.titulo,
                    p.cliente.nombre_completo(),
                    p.fecha_prestamo.strftime("%d/%m/%Y"),
                    p.fecha_devolucion_esperada.strftime("%d/%m/%Y"),
                    devuelto_str,
                    estado.value,
                ),
                tags=(tag,),
            )
        self._lbl_status.config(text=f"{len(prestamos)} préstamo(s) mostrado(s)")

    def _nuevo_prestamo(self):
        libros_disp = self._bsvc.obtener_libros_disponibles()
        clientes_act = self._bsvc.obtener_clientes_activos()

        if not libros_disp:
            messagebox.showwarning("Sin libros", "No hay libros disponibles para prestar.")
            return
        if not clientes_act:
            messagebox.showwarning("Sin clientes", "No hay clientes activos registrados.")
            return

        dialogo = _DialogNuevoPrestamo(self, libros_disp, clientes_act)
        self.wait_window(dialogo)
        if dialogo.resultado:
            isbn, dni, dias = dialogo.resultado
            try:
                prestamo = self._psvc.prestar_libro(isbn, dni, dias)
                self.actualizar()
                self._on_update()
                messagebox.showinfo(
                    "Éxito",
                    f"Préstamo registrado.\nID: {prestamo.id}\n"
                    f"Vence: {prestamo.fecha_devolucion_esperada.strftime('%d/%m/%Y')}",
                )
            except (LibroNoDisponibleError, ClienteNoEncontradoError,
                    ClienteInactivoError, LibroNoEncontradoError) as e:
                messagebox.showerror("Error", str(e))

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
            self._on_update()
            messagebox.showinfo("Éxito", "Devolución registrada correctamente.")
        except (PrestamoNoEncontradoError, PrestamoYaDevueltoError) as e:
            messagebox.showerror("Error", str(e))


class _DialogNuevoPrestamo(tk.Toplevel):
    def __init__(self, parent, libros, clientes):
        super().__init__(parent)
        self.title("Nuevo Préstamo")
        self.resizable(False, False)
        self.resultado = None
        self._libros   = libros
        self._clientes = clientes
        self._construir_ui()
        self.transient(parent)
        self.grab_set()
        self._centrar()

    def _centrar(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - self.winfo_width() // 2
        y = self.winfo_screenheight() // 2 - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")

    def _construir_ui(self):
        f = ttk.Frame(self, padding=24)
        f.pack(fill="both", expand=True)

        # Libro
        ttk.Label(f, text="Libro *").grid(row=0, column=0, sticky="w", pady=6)
        self._libros_map = {
            f"[{l.isbn}] {l.titulo}": l.isbn for l in self._libros
        }
        self._var_libro = tk.StringVar()
        cb_libro = ttk.Combobox(
            f, textvariable=self._var_libro,
            values=list(self._libros_map.keys()),
            state="readonly", width=40,
        )
        cb_libro.grid(row=0, column=1, padx=(12, 0), pady=6)

        # Cliente
        ttk.Label(f, text="Cliente *").grid(row=1, column=0, sticky="w", pady=6)
        self._clientes_map = {
            f"[{c.dni}] {c.nombre_completo()}": c.dni for c in self._clientes
        }
        self._var_cliente = tk.StringVar()
        cb_cliente = ttk.Combobox(
            f, textvariable=self._var_cliente,
            values=list(self._clientes_map.keys()),
            state="readonly", width=40,
        )
        cb_cliente.grid(row=1, column=1, padx=(12, 0), pady=6)

        # Días
        ttk.Label(f, text="Días de préstamo").grid(row=2, column=0, sticky="w", pady=6)
        self._var_dias = tk.IntVar(value=14)
        ttk.Spinbox(f, from_=1, to=90, textvariable=self._var_dias, width=6).grid(
            row=2, column=1, padx=(12, 0), pady=6, sticky="w"
        )

        btn_f = ttk.Frame(f)
        btn_f.grid(row=3, column=0, columnspan=2, pady=(18, 0))
        ttk.Button(btn_f, text="Confirmar", command=self._guardar).pack(side="left", padx=6)
        ttk.Button(btn_f, text="Cancelar",  command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda _: self._guardar())
        self.bind("<Escape>", lambda _: self.destroy())

    def _guardar(self):
        libro_str   = self._var_libro.get()
        cliente_str = self._var_cliente.get()
        if not libro_str or not cliente_str:
            messagebox.showerror(
                "Error", "Seleccione un libro y un cliente.", parent=self
            )
            return
        isbn = self._libros_map[libro_str]
        dni  = self._clientes_map[cliente_str]
        dias = self._var_dias.get()
        self.resultado = (isbn, dni, dias)
        self.destroy()
