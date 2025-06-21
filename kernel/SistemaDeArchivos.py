import os

class SistemaArchivos:
    def __init__(self, directorio_base):
        self.directorio_base = os.path.abspath(directorio_base)
        if not os.path.exists(self.directorio_base):
            os.makedirs(self.directorio_base)

    def ruta_completa(self, nombre):
        ruta = os.path.abspath(os.path.join(self.directorio_base, nombre))
        if not ruta.startswith(self.directorio_base):
            raise ValueError("Ruta fuera del directorio base no permitida")
        return ruta

    def ruta_relativa(self, ruta_absoluta):
        return os.path.relpath(ruta_absoluta, self.directorio_base)

    def crear_archivo(self, nombre, contenido=""):
        try:
            ruta = self.ruta_completa(nombre)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            return f"Archivo '{nombre}' creado."
        except Exception as e:
            return f"Error al crear archivo '{nombre}': {e}"

    def leer_archivo(self, nombre):
        try:
            ruta = self.ruta_completa(nombre)
            if os.path.isfile(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    return f.read()
            return f"Archivo '{nombre}' no existe."
        except Exception as e:
            return f"Error al leer archivo '{nombre}': {e}"

    def eliminar_archivo(self, nombre):
        try:
            ruta = self.ruta_completa(nombre)
            if os.path.isfile(ruta):
                os.remove(ruta)
                return f"Archivo '{nombre}' eliminado."
            return f"Archivo '{nombre}' no existe."
        except Exception as e:
            return f"Error al eliminar archivo '{nombre}': {e}"

    def listar_archivos(self):
        resultado = []
        for carpeta_actual, subdirs, archivos in os.walk(self.directorio_base):
            for nombre in subdirs:
                ruta_abs = os.path.join(carpeta_actual, nombre)
                ruta_rel = self.ruta_relativa(ruta_abs)
                resultado.append(f"[DIR]  {ruta_rel}")
            for nombre in archivos:
                ruta_abs = os.path.join(carpeta_actual, nombre)
                ruta_rel = self.ruta_relativa(ruta_abs)
                resultado.append(f"[FILE] {ruta_rel}")
        return sorted(resultado)

    def crear_carpeta(self, nombre):
        try:
            ruta = self.ruta_completa(nombre)
            os.makedirs(ruta, exist_ok=True)
            return f"Carpeta '{nombre}' creada exitosamente."
        except Exception as e:
            return f"Error al crear carpeta '{nombre}': {e}"

    def mover_archivo(self, origen, destino):
        try:
            ruta_origen = self.ruta_completa(origen)
            ruta_destino = self.ruta_completa(destino)
            if os.path.exists(ruta_origen):
                os.rename(ruta_origen, ruta_destino)
                return f"Archivo movido de '{origen}' a '{destino}'."
            return f"Archivo '{origen}' no existe."
        except Exception as e:
            return f"Error al mover archivo: {e}"
