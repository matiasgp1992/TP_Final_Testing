import tkinter as tk
from tkinter import ttk, messagebox

from ...services.biblioteca_service import BibliotecaService
from ...exceptions import (
    AutorNoEncontradoError,
    LibroYaExisteError,
    LibroNoEncontradoError,
    LibroPrestadoError,
)


class LibrosFrame(ttk.Frame):
    def __init__(self, parent, biblioteca_svc: BibliotecaService):
        super().__init__(parent)
        self._svc = biblioteca_svc
        self._construir_ui()
        self.actualizar()

    def _construir_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=12, pady=(12, 0))

        ttk.Button(
            toolbar, text="+ Nuevo Libro",
            command=self._nuevo_libro,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            toolbar, text="Dar de Baja",
            command=self._dar_de_baja,
        ).pack(side="left", padx=(0, 16))

        ttk.Label(toolbar, text="Buscar:").pack(side="left", padx=(0, 4))
        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", lambda *_: self.actualizar())
        ttk.Entry(toolbar, textvariable=self._var_busqueda, width=22).pack(side="left")

        # Filtro estado
        ttk.Label(toolbar, text="Estado:").pack(side="left", padx=(16, 4))
        self._var_filtro = tk.StringVar(value="Todos")
        cb = ttk.Combobox(
            toolbar, textvariable=self._var_filtro,
            values=["Todos", "Disponible", "Prestado"],
            state="readonly", width=12,
        )
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda _: self.actualizar())

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill="both", expand=True, padx=12, pady=10)

        cols = ("isbn", "titulo", "editorial", "autor", "estado")
        self._tree = ttk.Treeview(
            frame_tree, columns=cols, show="headings", selectmode="browse"
        )
        self._tree.heading("isbn",      text="ISBN")
        self._tree.heading("titulo",    text="Título")
        self._tree.heading("editorial", text="Editorial")
        self._tree.heading("autor",     text="Autor")
        self._tree.heading("estado",    text="Estado")
        self._tree.column("isbn",      width=140, anchor="w")
        self._tree.column("titulo",    width=250, anchor="w")
        self._tree.column("editorial", width=160, anchor="w")
        self._tree.column("autor",     width=200, anchor="w")
        self._tree.column("estado",    width=100, anchor="center")

        self._tree.tag_configure("prestado",   background="#fff5f5", foreground="#c53030")
        self._tree.tag_configure("disponible", background="#f0fff4", foreground="#276749")

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
        libros = self._svc.obtener_libros()

        if filtro == "Disponible":
            libros = [l for l in libros if l.esta_disponible()]
        elif filtro == "Prestado":
            libros = [l for l in libros if not l.esta_disponible()]

        if busqueda:
            libros = [
                l for l in libros
                if busqueda in l.titulo.lower()
                or busqueda in l.isbn.lower()
                or busqueda in l.autor.nombre_completo().lower()
            ]

        for l in libros:
            tag = "disponible" if l.esta_disponible() else "prestado"
            self._tree.insert(
                "", "end",
                iid=l.isbn,
                values=(
                    l.isbn, l.titulo, l.editorial,
                    l.autor.nombre_completo(),
                    l.estado.value,
                ),
                tags=(tag,),
            )
        self._lbl_status.config(text=f"{len(libros)} libro(s) mostrado(s)")

    def _nuevo_libro(self):
        autores = self._svc.obtener_autores()
        if not autores:
            messagebox.showwarning(
                "Sin autores",
                "Primero debe registrar al menos un autor en la pestaña Autores.",
            )
            return
        dialogo = _DialogLibro(self, autores)
        self.wait_window(dialogo)
        if dialogo.resultado:
            isbn, titulo, editorial, nombre_a, apellido_a = dialogo.resultado
            try:
                self._svc.agregar_libro(isbn, titulo, editorial, nombre_a, apellido_a)
                self.actualizar()
                messagebox.showinfo("Éxito", f"Libro '{titulo}' registrado correctamente.")
            except (LibroYaExisteError, AutorNoEncontradoError) as e:
                messagebox.showerror("Error", str(e))
            except ValueError as e:
                messagebox.showerror("Datos inválidos", str(e))

    def _dar_de_baja(self):
        sel = self._tree.focus()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione un libro de la lista.")
            return
        valores = self._tree.item(sel, "values")
        isbn, titulo = valores[0], valores[1]
        if not messagebox.askyesno(
            "Confirmar baja",
            f"¿Desea dar de baja el libro '{titulo}'?",
        ):
            return
        try:
            self._svc.dar_de_baja_libro(isbn)
            self.actualizar()
            messagebox.showinfo("Éxito", f"Libro '{titulo}' dado de baja.")
        except (LibroNoEncontradoError, LibroPrestadoError) as e:
            messagebox.showerror("Error", str(e))


class _DialogLibro(tk.Toplevel):
    def __init__(self, parent, autores):
        super().__init__(parent)
        self.title("Nuevo Libro")
        self.resizable(False, False)
        self.resultado = None
        self._autores = autores
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

        campos_texto = [
            ("ISBN *",       "isbn"),
            ("Título *",     "titulo"),
            ("Editorial *",  "editorial"),
        ]
        self._vars = {}
        for i, (label, key) in enumerate(campos_texto):
            ttk.Label(f, text=label).grid(row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            self._vars[key] = var
            ttk.Entry(f, textvariable=var, width=36).grid(
                row=i, column=1, padx=(12, 0), pady=6
            )

        # Autor (combobox)
        row_autor = len(campos_texto)
        ttk.Label(f, text="Autor *").grid(row=row_autor, column=0, sticky="w", pady=6)
        opciones = [f"{a.nombre} {a.apellido}" for a in self._autores]
        self._var_autor = tk.StringVar()
        cb = ttk.Combobox(
            f, textvariable=self._var_autor,
            values=opciones, state="readonly", width=34,
        )
        cb.grid(row=row_autor, column=1, padx=(12, 0), pady=6)

        btn_f = ttk.Frame(f)
        btn_f.grid(row=row_autor + 1, column=0, columnspan=2, pady=(18, 0))
        ttk.Button(btn_f, text="Guardar",  command=self._guardar).pack(side="left", padx=6)
        ttk.Button(btn_f, text="Cancelar", command=self.destroy).pack(side="left", padx=6)

        self.bind("<Return>", lambda _: self._guardar())
        self.bind("<Escape>", lambda _: self.destroy())

    def _guardar(self):
        isbn      = self._vars["isbn"].get().strip()
        titulo    = self._vars["titulo"].get().strip()
        editorial = self._vars["editorial"].get().strip()
        autor_str = self._var_autor.get().strip()

        if not isbn or not titulo or not editorial or not autor_str:
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self)
            return

        partes = autor_str.split(" ", 1)
        nombre_a  = partes[0]
        apellido_a = partes[1] if len(partes) > 1 else ""
        self.resultado = (isbn, titulo, editorial, nombre_a, apellido_a)
        self.destroy()
