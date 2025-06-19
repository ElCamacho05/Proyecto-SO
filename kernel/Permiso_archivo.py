# kernel/Permiso_archivo.py

def tiene_permiso(rol, recurso, accion):
    """
    Verifica si un rol tiene permiso para realizar cierta acción sobre un recurso.

    :param rol: str, 'admin' o 'invitado'
    :param recurso: str, como 'terminal', 'calculadora', 'archivo_txt', 'bloc_notas'
    :param accion: str, como 'leer', 'escribir', 'ejecutar'
    :return: bool, True si tiene permiso, False si no
    """

    permisos = {
        "admin": {
            "terminal": ["leer", "escribir", "ejecutar"],
            "calculadora": ["ejecutar"],
            "archivo_txt": ["leer", "escribir"],
            "bloc_notas": ["leer", "escribir", "ejecutar"],
            "explorador_archivos": ["leer", "escribir", "ejecutar"]
        },
        "invitado": {
            "terminal": ["leer"],  # Solo lectura, sin ejecutar comandos
            "calculadora": ["ejecutar"],
            "archivo_txt": ["leer"],
            "bloc_notas": ["leer"],  # No puede escribir o ejecutar
            "explorador_archivos": ["leer"]
        }
    }

    rol = rol.lower()
    recurso = recurso.lower()
    accion = accion.lower()

    return accion in permisos.get(rol, {}).get(recurso, [])
