import tkinter as tk
from tkinter import ttk, messagebox

from ...services.biblioteca_service import BibliotecaService
from ...services.prestamo_service import PrestamoService
from ...exceptions import (
    ClienteYaExisteError,
    ClienteNoEncontradoError,
    ClienteInactivoError,
)


class ClientesFrame(ttk.Frame):
    def __init__(self, parent, biblioteca_svc: BibliotecaService, prestamo_svc: PrestamoService):
        super().__init__(parent)
        self._svc  = biblioteca_svc
        self._psvc = prestamo_svc
        self._construir_ui()
        self.actualizar()

    def _construir_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(toolbar, text="+ Nuevo Cliente", command=self._nuevo_cliente).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(toolbar, text="Dar de Baja", command=self._dar_de_baja).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(toolbar, text="Ver Préstamos", command=self._ver_prestamos).pack(
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
            values=["Todos", "Activo", "Inactivo"],
            state="readonly", width=10,
        )
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda _: self.actualizar())

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill="both", expand=True, padx=12, pady=10)

        cols = ("dni", "nombre", "apellido", "estado")
        self._tree = ttk.Treeview(
            frame_tree, columns=cols, show="headings", selectmode="browse"
        )
        self._tree.heading("dni",      text="DNI")
        self._tree.heading("nombre",   text="Nombre")
        self._tree.heading("apellido", text="Apellido")
        self._tree.heading("estado",   text="Estado")
        self._tree.column("dni",      width=130, anchor="w")
        self._tree.column("nombre",   width=220, anchor="w")
        self._tree.column("apellido", width=220, anchor="w")
        self._tree.column("estado",   width=100, anchor="center")

        self._tree.tag_configure("inactivo", background="#f7fafc", foreground="#a0aec0")
        self._tree.tag_configure("activo",   foreground="#2d3748")

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
        clientes = self._svc.obtener_clientes()

        if filtro == "Activo":
            clientes = [c for c in clientes if c.activo]
        elif filtro == "Inactivo":
            clientes = [c for c in clientes if not c.activo]

        if busqueda:
            clientes = [
                c for c in clientes
                if busqueda in c.nombre.lower()
                or busqueda in c.apellido.lower()
                or busqueda in c.dni
            ]

        for c in clientes:
            tag = "activo" if c.activo else "inactivo"
            estado_txt = "Activo" if c.activo else "Inactivo"
            self._tree.insert(
                "", "end", iid=c.dni,
                values=(c.dni, c.nombre, c.apellido, estado_txt),
                tags=(tag,),
            )
        self._lbl_status.config(text=f"{len(clientes)} cliente(s) mostrado(s)")

    def _nuevo_cliente(self):
        dialogo = _DialogCliente(self)
        self.wait_window(dialogo)
        if dialogo.resultado:
            dni, nombre, apellido = dialogo.resultado
            try:
                self._svc.agregar_cliente(dni, nombre, apellido)
                self.actualizar()
                messagebox.showinfo("Éxito", f"Cliente '{nombre} {apellido}' registrado.")
            except ClienteYaExisteError as e:
                messagebox.showerror("Error", str(e))
            except ValueError as e:
                messagebox.showerror("Datos inválidos", str(e))

    def _dar_de_baja(self):
        sel = self._tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione un cliente de la lista.")
            return
        valores = self._tree.item(sel, "values")
        dni, nombre, apellido = valores[0], valores[1], valores[2]
        if not messagebox.askyesno(
            "Confirmar baja",
            f"¿Desea dar de baja a '{nombre} {apellido}'?",
        ):
            return
        try:
            self._svc.dar_de_baja_cliente(dni)
            self.actualizar()
            messagebox.showinfo("Éxito", f"Cliente '{nombre} {apellido}' dado de baja.")
        except (ClienteNoEncontradoError, ClienteInactivoError) as e:
            messagebox.showerror("Error", str(e))

    def _ver_prestamos(self):
        sel = self._tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione un cliente de la lista.")
            return
        valores = self._tree.item(sel, "values")
        dni, nombre, apellido = valores[0], valores[1], valores[2]
        prestamos = self._psvc.obtener_prestamos_de_cliente(dni)
        activos = [p for p in prestamos if not p.esta_devuelto()]
        _DialogPrestamosCliente(self, f"{nombre} {apellido}", activos)


class _DialogCliente(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nuevo Cliente")
        self.resizable(False, False)
        self.resultado = None
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

        campos = [("DNI *", "dni"), ("Nombre *", "nombre"), ("Apellido *", "apellido")]
        self._vars = {}
        for i, (label, key) in enumerate(campos):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            self._vars[key] = var
            ttk.Entry(f, textvariable=var, width=32).grid(
                row=i, column=1, padx=(12, 0), pady=6
            )

        btn_f = ttk.Frame(f)
        btn_f.grid(row=len(campos), column=0, columnspan=2, pady=(18, 0))
        ttk.Button(btn_f, text="Guardar",  command=self._guardar).pack(side="left", padx=6)
        ttk.Button(btn_f, text="Cancelar", command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda _: self._guardar())
        self.bind("<Escape>", lambda _: self.destroy())

    def _guardar(self):
        dni      = self._vars["dni"].get().strip()
        nombre   = self._vars["nombre"].get().strip()
        apellido = self._vars["apellido"].get().strip()
        if not dni or not nombre or not apellido:
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self)
            return
        self.resultado = (dni, nombre, apellido)
        self.destroy()


class _DialogPrestamosCliente(tk.Toplevel):
    def __init__(self, parent, nombre_cliente: str, prestamos):
        super().__init__(parent)
        self.title(f"Préstamos activos — {nombre_cliente}")
        self.geometry("700x380")
        self.resizable(True, True)
        self._construir_ui(nombre_cliente, prestamos)
        self.transient(parent)
        self.grab_set()
        self._centrar()

    def _centrar(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - self.winfo_width() // 2
        y = self.winfo_screenheight() // 2 - self.winfo_height() // 2
        self.geometry(f"+{x}+{y}")

    def _construir_ui(self, nombre_cliente, prestamos):
        ttk.Label(
            self,
            text=f"Préstamos activos de: {nombre_cliente}",
            font=("Segoe UI", 11, "bold"),
        ).pack(padx=12, pady=(12, 6), anchor="w")

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "libro", "prestado", "vence", "estado")
        tree = ttk.Treeview(frame_tree, columns=cols, show="headings")
        tree.heading("id",       text="ID")
        tree.heading("libro",    text="Libro")
        tree.heading("prestado", text="Fecha préstamo")
        tree.heading("vence",    text="Vence")
        tree.heading("estado",   text="Estado")
        tree.column("id",       width=70,  anchor="center")
        tree.column("libro",    width=260, anchor="w")
        tree.column("prestado", width=110, anchor="center")
        tree.column("vence",    width=110, anchor="center")
        tree.column("estado",   width=90,  anchor="center")

        tree.tag_configure("vencido", background="#fff5f5", foreground="#c53030")

        for p in prestamos:
            tag = "vencido" if p.esta_vencido() else ""
            tree.insert(
                "", "end",
                values=(
                    p.id, p.libro.titulo,
                    p.fecha_prestamo.strftime("%d/%m/%Y"),
                    p.fecha_devolucion_esperada.strftime("%d/%m/%Y"),
                    p.estado().value,
                ),
                tags=(tag,),
            )

        sb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if not prestamos:
            ttk.Label(self, text="Este cliente no tiene préstamos activos.",
                      foreground="#718096").pack(pady=4)

        ttk.Button(self, text="Cerrar", command=self.destroy).pack(pady=10)
