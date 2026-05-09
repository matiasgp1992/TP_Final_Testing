import tkinter as tk
from tkinter import ttk

from ..repositories.autor_repository import AutorRepository
from ..repositories.libro_repository import LibroRepository
from ..repositories.cliente_repository import ClienteRepository
from ..repositories.prestamo_repository import PrestamoRepository
from ..services.biblioteca_service import BibliotecaService
from ..services.prestamo_service import PrestamoService

from .frames.autores_frame import AutoresFrame
from .frames.libros_frame import LibrosFrame
from .frames.clientes_frame import ClientesFrame
from .frames.prestamos_frame import PrestamosFrame
from .frames.vencidos_frame import VencidosFrame

COLOR_HEADER = "#1a365d"
COLOR_ACCENT = "#2b6cb0"


class BibliotecaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biblioteca Barrial — Sistema de Préstamos")
        self.geometry("1150x720")
        self.minsize(950, 620)
        self.configure(bg="#f7fafc")

        self._init_repos()
        self._init_servicios()
        self._init_estilos()
        self._construir_ui()

    def _init_repos(self):
        self._autor_repo = AutorRepository()
        self._libro_repo = LibroRepository()
        self._cliente_repo = ClienteRepository()
        self._prestamo_repo = PrestamoRepository()

    def _init_servicios(self):
        self.biblioteca_svc = BibliotecaService(
            self._autor_repo,
            self._libro_repo,
            self._cliente_repo,
            self._prestamo_repo,
        )
        self.prestamo_svc = PrestamoService(
            self._libro_repo,
            self._cliente_repo,
            self._prestamo_repo,
        )

    def _init_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TNotebook", background="#e2e8f0", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=[14, 7],
            font=("Segoe UI", 10, "bold"),
            background="#cbd5e0",
            foreground="#2d3748",
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLOR_ACCENT)],
            foreground=[("selected", "white")],
        )

        style.configure(
            "Treeview",
            background="white",
            foreground="#2d3748",
            rowheight=30,
            fieldbackground="white",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background=COLOR_HEADER,
            foreground="white",
            relief="flat",
            padding=[5, 6],
        )
        style.map(
            "Treeview",
            background=[("selected", "#bee3f8")],
            foreground=[("selected", "#1a365d")],
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=[12, 6],
        )
        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=[12, 6],
        )
        style.configure("TLabel", font=("Segoe UI", 9))
        style.configure("TEntry", font=("Segoe UI", 9))

    def _construir_ui(self):
        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="  Biblioteca Barrial",
            font=("Segoe UI", 17, "bold"),
            bg=COLOR_HEADER,
            fg="white",
        ).pack(side="left", padx=20, pady=12)

        tk.Label(
            header,
            text="Sistema de Préstamos",
            font=("Segoe UI", 10),
            bg=COLOR_HEADER,
            fg="#90cdf4",
        ).pack(side="left", pady=18)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.frame_autores = AutoresFrame(self.notebook, self.biblioteca_svc)
        self.frame_libros = LibrosFrame(self.notebook, self.biblioteca_svc)
        self.frame_clientes = ClientesFrame(
            self.notebook, self.biblioteca_svc, self.prestamo_svc
        )
        self.frame_prestamos = PrestamosFrame(
            self.notebook,
            self.biblioteca_svc,
            self.prestamo_svc,
            on_update=self._on_prestamo_cambio,
        )
        self.frame_vencidos = VencidosFrame(
            self.notebook,
            self.prestamo_svc,
            on_devolucion=self._on_prestamo_cambio,
        )

        self.notebook.add(self.frame_autores,  text="  Autores  ")
        self.notebook.add(self.frame_libros,   text="  Libros  ")
        self.notebook.add(self.frame_clientes, text="  Clientes  ")
        self.notebook.add(self.frame_prestamos, text="  Préstamos  ")
        self.notebook.add(self.frame_vencidos,  text="  Vencidos  ")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_cambiado)
        self._actualizar_tab_vencidos()

    def _on_tab_cambiado(self, _event):
        indice = self.notebook.index(self.notebook.select())
        frames = [
            self.frame_autores,
            self.frame_libros,
            self.frame_clientes,
            self.frame_prestamos,
            self.frame_vencidos,
        ]
        frames[indice].actualizar()

    def _on_prestamo_cambio(self):
        self.frame_libros.actualizar()
        self.frame_clientes.actualizar()
        self.frame_vencidos.actualizar()
        self._actualizar_tab_vencidos()

    def _actualizar_tab_vencidos(self):
        n = len(self.prestamo_svc.obtener_vencidos())
        texto = "  Vencidos  " if n == 0 else f"  ⚠ Vencidos ({n})  "
        self.notebook.tab(4, text=texto)
