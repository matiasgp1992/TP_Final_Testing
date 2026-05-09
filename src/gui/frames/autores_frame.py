import tkinter as tk
from tkinter import ttk, messagebox

from ...services.biblioteca_service import BibliotecaService
from ...exceptions import AutorYaExisteError


class AutoresFrame(ttk.Frame):
    def __init__(self, parent, biblioteca_svc: BibliotecaService):
        super().__init__(parent)
        self._svc = biblioteca_svc
        self._construir_ui()
        self.actualizar()

    def _construir_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(
            toolbar, text="+ Nuevo Autor",
            command=self._nuevo_autor,
        ).pack(side="left", padx=(0, 8))

        ttk.Label(toolbar, text="Buscar:").pack(side="left", padx=(16, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *_: self.actualizar())
        ttk.Entry(toolbar, textvariable=self._var_busqueda, width=22).pack(side="left")

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill="both", expand=True, padx=12, pady=10)

        cols = ("nombre", "apellido", "nacionalidad")
        self._tree = ttk.Treeview(
            frame_tree, columns=cols, show="headings", selectmode="browse"
        )
        self._tree.heading("nombre",       text="Nombre")
        self._tree.heading("apellido",     text="Apellido")
        self._tree.heading("nacionalidad", text="Nacionalidad")
        self._tree.column("nombre",       width=220, anchor="w")
        self._tree.column("apellido",     width=220, anchor="w")
        self._tree.column("nacionalidad", width=220, anchor="w")

        sb = ttk.Scrollbar(frame_tree, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._lbl_status = ttk.Label(self, text="", foreground="#718096")
        self._lbl_status.pack(anchor="w", padx=12, pady=(0, 6))

    def actualizar(self, *_):
        busqueda = self._var_busqueda.get().lower()
        self._tree.delete(*self._tree.get_children())
        autores = self._svc.obtener_autores()
        if busqueda:
            autores = [
                a for a in autores
                if busqueda in a.nombre.lower() or busqueda in a.apellido.lower()
            ]
        for a in autores:
            self._tree.insert(
                "", "end",
                values=(a.nombre, a.apellido, a.nacionalidad or "—"),
            )
        self._lbl_status.config(text=f"{len(autores)} autor(es) registrado(s)")

    def _nuevo_autor(self):
        dialogo = _DialogAutor(self)
        self.wait_window(dialogo)
        if dialogo.resultado:
            nombre, apellido, nacionalidad = dialogo.resultado
            try:
                self._svc.agregar_autor(nombre, apellido, nacionalidad)
                self.actualizar()
                messagebox.showinfo(
                    "Éxito", f"Autor '{nombre} {apellido}' registrado correctamente."
                )
            except AutorYaExisteError as e:
                messagebox.showerror("Error", str(e))
            except ValueError as e:
                messagebox.showerror("Datos inválidos", str(e))


class _DialogAutor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nuevo Autor")
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

        campos = [
            ("Nombre *",     "nombre"),
            ("Apellido *",   "apellido"),
            ("Nacionalidad", "nacionalidad"),
        ]
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
        ttk.Button(btn_f, text="Guardar", command=self._guardar).pack(side="left", padx=6)
        ttk.Button(btn_f, text="Cancelar", command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda _: self._guardar())
        self.bind("<Escape>", lambda _: self.destroy())

    def _guardar(self):
        nombre      = self._vars["nombre"].get().strip()
        apellido    = self._vars["apellido"].get().strip()
        nacionalidad = self._vars["nacionalidad"].get().strip()
        if not nombre or not apellido:
            messagebox.showerror("Error", "Nombre y apellido son obligatorios.", parent=self)
            return
        self.resultado = (nombre, apellido, nacionalidad)
        self.destroy()
