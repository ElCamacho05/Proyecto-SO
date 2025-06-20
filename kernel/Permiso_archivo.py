# kernel/Permiso_archivo.py

def tiene_permiso(rol, recurso, accion):
    permisos = {
        "admin": {
            "terminal": ["leer", "escribir", "ejecutar"],
            "calculadora": ["ejecutar"],
            "archivo_txt": ["leer", "escribir"],
            "bloc_notas": ["leer", "escribir", "ejecutar"],
            "explorador_archivos": ["leer", "escribir", "ejecutar"]
        },
        "invitado": {
            "terminal": ["leer"],  # No puede ejecutar comandos
            "calculadora": ["ejecutar"],
            "archivo_txt": ["leer"],
            "bloc_notas": ["leer"],
            "explorador_archivos": ["leer"]
        }
    }

    if rol is None:
        return False
    rol = rol.lower()
    recurso = recurso.lower()
    accion = accion.lower()

    return accion in permisos.get(rol, {}).get(recurso, [])

