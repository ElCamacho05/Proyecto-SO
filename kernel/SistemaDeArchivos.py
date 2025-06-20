# kernel/sistema_archivos.py
import os

class SistemaArchivos:
    def __init__(self, directorio_base="disco_virtual"):
        self.directorio_base = directorio_base
        if not os.path.exists(self.directorio_base):
            os.makedirs(self.directorio_base)

    def ruta_completa(self, nombre):
        return os.path.join(self.directorio_base, nombre)

    def crear_archivo(self, nombre, contenido=""):
        ruta = self.ruta_completa(nombre)
        with open(ruta, "w") as f:
            f.write(contenido)
        return f"Archivo '{nombre}' creado."

    def leer_archivo(self, nombre):
        ruta = self.ruta_completa(nombre)
        if os.path.exists(ruta):
            with open(ruta, "r") as f:
                return f.read()
        return f"Archivo '{nombre}' no existe."

    def eliminar_archivo(self, nombre):
        ruta = self.ruta_completa(nombre)
        if os.path.exists(ruta):
            os.remove(ruta)
            return f"Archivo '{nombre}' eliminado."
        return f"Archivo '{nombre}' no existe."

    def listar_archivos(self):
        return os.listdir(self.directorio_base)

    def crear_carpeta(self, nombre):
        """
        Crea una carpeta (o estructura de carpetas) dentro del disco virtual.
        Ejemplo: 'carpeta1/subcarpeta2' creará ambas si no existen.
        """
        ruta = self.ruta_completa(nombre)
        try:
            os.makedirs(ruta, exist_ok=True)
            return f"Carpeta '{nombre}' creada exitosamente."
        except Exception as e:
            return f"Error al crear carpeta '{nombre}': {e}"

    def mover_archivo(self, origen, destino):
        ruta_origen = self.ruta_completa(origen)
        ruta_destino = self.ruta_completa(destino)
        if os.path.exists(ruta_origen):
            os.rename(ruta_origen, ruta_destino)
            return f"Archivo movido de '{origen}' a '{destino}'."
        return f"Archivo '{origen}' no existe."