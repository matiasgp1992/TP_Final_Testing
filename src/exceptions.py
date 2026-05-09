class BibliotecaError(Exception):
    pass


class AutorNoEncontradoError(BibliotecaError):
    pass


class AutorYaExisteError(BibliotecaError):
    pass


class LibroNoEncontradoError(BibliotecaError):
    pass


class LibroYaExisteError(BibliotecaError):
    pass


class LibroNoDisponibleError(BibliotecaError):
    pass


class LibroPrestadoError(BibliotecaError):
    pass


class ClienteNoEncontradoError(BibliotecaError):
    pass


class ClienteYaExisteError(BibliotecaError):
    pass


class ClienteInactivoError(BibliotecaError):
    pass


class PrestamoNoEncontradoError(BibliotecaError):
    pass


class PrestamoYaDevueltoError(BibliotecaError):
    pass
