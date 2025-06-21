import random
import tkinter as tk
import time
import os

from kernel.Memoria import Memoria
from kernel.Planificador import Planificador
from kernel.SistemaDeArchivos import SistemaArchivos
from kernel.Proceso import GestorPID
from gui.data.funciones import funciones_disponibles

class TerminalSO:
    def __init__(self, terminal_output, frame_terminal, boton_tarea, entrada, ventanas_abiertas, procesos_activos=None, planificador=None):
        self.memoria = Memoria()
        directorio_actual_archivo = os.path.dirname(os.path.abspath(__file__))
        self.ROOT_DIR = os.path.abspath(os.path.join(directorio_actual_archivo, "..", "apps", "MiPC"))
        self.directorio_actual = self.ROOT_DIR  # Usamos ROOT_DIR aquí

        self.procesos_activos = procesos_activos if procesos_activos is not None else {}

        self.terminal_output = terminal_output
        self.frame_terminal = frame_terminal
        self.boton_tarea = boton_tarea
        self.entrada = entrada
        self.planificador = Planificador() if not planificador else planificador
        self.ventanas_abiertas = ventanas_abiertas
        self.fs = SistemaArchivos(self.ROOT_DIR)

        self.comandos = {
            "ayuda": self.mostrar_ayuda,
            "borrar_archivo": self.borrar_archivo,
            "cd": self.cambiar_directorio,
            "crear_archivo": self.crear_archivo,
            "crear_carpeta": self.crear_carpeta,
            "iniciar": self.iniciar_proceso,
            "leer_archivo": self.leer_archivo,
            "limpiar": self.limpiar_salida,
            "listar": self.listar_procesos,
            "listar_archivos": self.listar_archivos,
            "mover_archivo": self.mover_archivo,
            "memoria": self.mostrar_memoria,
            "planificar_fifo": self.planificar_fifo,
            "planificar_prioridad": self.planificar_prioridad,
            "planificar_rr": self.planificar_rr,
            "salir": self.cerrar_terminal,
            "terminar": self.terminar_proceso
        }

        self.argc = {
            "ayuda": 0,
            "borrar_archivo": 1,
            "cd": 1,
            "crear_archivo": -1,
            "crear_carpeta": 1,
            "iniciar": -1,
            "leer_archivo": 1,
            "limpiar": 0,
            "listar": 0,
            "listar_archivos": 0,
            "mover_archivo": 2,
            "memoria": 0,
            "planificar_fifo": 0,
            "planificar_prioridad": 0,
            "planificar_rr": 0,
            "salir": 0,
            "terminar": 1
        }

    def escribir(self, texto):
        try:
            self.terminal_output.config(state="normal")
            self.terminal_output.insert(tk.END, texto + "\n")
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state="disabled")
        except tk.TclError:
            pass

    def mostrar_ayuda(self):
        comandos = [
            "ayuda - Muestra esta ayuda",
            "borrar_archivo <nombre> - Elimina un archivo",
            "cd <ruta> - Cambia el directorio actual",
            "crear_archivo <nombre> <contenido> - Crea un archivo .txt",
            "crear_carpeta <nombre> - Crea una carpeta en el directorio especificado",
            "iniciar <func/None> - Inicia un nuevo proceso",
            "leer_archivo <nombre> - Muestra el contenido de un archivo",
            "limpiar - Limpia la salida",
            "listar - Lista todos los procesos",
            "listar_archivos - Muestra los archivos existentes",
            "mover_archivo <origen> <destino> - Mueve un archivo a una ubicación deseada",
            "memoria - Muestra estado de la memoria",
            "planificar_fifo - Ejecuta el siguiente proceso FIFO",
            "planificar_prioridad - Ejecuta el siguiente proceso por prioridad",
            "planificar_rr - Ejecuta el siguiente proceso Round Robin",
            "salir - Cierra esta terminal",
            "terminar <pid> - Termina un proceso"
        ]
        self.escribir("Comandos disponibles:")
        for cmd in comandos:
            self.escribir("  " + cmd)

    def limpiar_salida(self):
        try:
            self.terminal_output.config(state="normal")
            self.terminal_output.delete("1.0", tk.END)
            self.terminal_output.config(state="disabled")
        except tk.TclError:
            pass

    def cerrar_terminal(self):
        self.escribir("Cerrando terminal...")
        if self.frame_terminal in self.ventanas_abiertas:
            self.ventanas_abiertas.remove(self.frame_terminal)
        self.frame_terminal.destroy()
        self.boton_tarea.destroy()
        self.entrada.destroy()

    def ejecutar_comando(self, comando):
        partes = comando.strip().split()
        if not partes:
            return

        cmd = partes[0]
        args = partes[1:]

        if cmd in self.comandos:
            esperado = self.argc.get(cmd, -1)

            if esperado != -1 and len(args) != esperado:
                self.escribir(f"Error: '{cmd}' espera {esperado} argumento(s), pero recibió {len(args)}.")
                return
            if esperado == -1 and len(args) < 1:
                self.escribir(f"Error: '{cmd}' espera al menos 1 argumento.")
                return

            try:
                self.comandos[cmd](*args)
            except Exception as e:
                self.escribir(f"Error inesperado al ejecutar '{cmd}': {e}")
        else:
            self.escribir(f"Comando no reconocido: {cmd}. Escribe 'ayuda' para ver los comandos disponibles")

    def iniciar_proceso(self, *args):
        if len(args) > 1:
            self.escribir("Uso: iniciar [nombre_funcion]")
            return

        nombre_func = args[0] if args else None
        func = None

        if nombre_func and nombre_func != "None":
            if nombre_func not in funciones_disponibles:
                self.escribir(f"Error: Función '{nombre_func}' no reconocida. Funciones disponibles:")
                for k in funciones_disponibles:
                    self.escribir(f"* {k}")
                return
            func = funciones_disponibles[nombre_func]

        pid_int = GestorPID.obtener_pid()
        tam_int = random.randint(5, 20)
        asignado = self.memoria.asignar_memoria(pid_int, tam_int, func)

        if asignado:
            proceso_obj = next((p for p in self.memoria.procesos if p.pid == pid_int), None)
            if proceso_obj:
                proceso_obj.start()

            self.procesos_activos[pid_int] = {
                'tamanio': tam_int,
                'inicio': time.time(),
                'estado': 'Ejecutando',
                'prioridad': pid_int % 5
            }

            proceso = {'pid': pid_int, 'prioridad': self.procesos_activos[pid_int]['prioridad']}
            self.planificador.agregar_proceso_fifo(proceso)
            self.planificador.agregar_proceso_rr(proceso)
            self.planificador.agregar_proceso_prioridad(proceso)

            self.escribir(f"Proceso {pid_int} iniciado " +
                          (f"con función '{nombre_func}'" if func else "sin función"))
        else:
            self.escribir("Error: No se pudo asignar memoria")

    def terminar_proceso(self, pid):
        try:
            pid_int = int(pid)
            if pid_int not in self.procesos_activos:
                self.escribir(f"Error: No existe un proceso con PID {pid_int}")
                return
            self.memoria.liberar_memoria(pid_int)
            del self.procesos_activos[pid_int]
            self.escribir(f"Proceso {pid_int} terminado correctamente")
            self.planificador.eliminar_proceso(pid_int)
        except ValueError:
            self.escribir("Error: PID debe ser un número entero")

    def listar_procesos(self):
        if not self.procesos_activos:
            self.escribir("No hay procesos activos")
            return
        self.escribir("PID\tTamaño\tEstado\t\tTiempo (s)")
        for pid, info in self.procesos_activos.items():
            tiempo = int(time.time() - info['inicio'])
            self.escribir(f"{pid}\t{info['tamanio']}\t{info['estado']}\t\t{tiempo}")

    def mostrar_memoria(self):
        self.escribir(str(self.memoria))

    def planificar_fifo(self):
        resultado, pid = self.planificador.ejecutar_fifo()
        self.escribir(resultado)
        self.terminar_proceso(pid)

    def planificar_rr(self):
        resultado, pid = self.planificador.ejecutar_rr(quantum=3)
        self.escribir(resultado)
        self.terminar_proceso(pid)

    def planificar_prioridad(self):
        resultado, pid = self.planificador.ejecutar_prioridad()
        self.escribir(resultado)
        self.terminar_proceso(pid)

    def crear_archivo(self, nombre, *contenido):
        contenido = " ".join(contenido)
        msg = self.fs.crear_archivo(nombre, contenido)
        self.escribir(msg)

    def leer_archivo(self, nombre):
        try:
            ruta = os.path.abspath(os.path.join(self.directorio_actual, nombre))
            if not ruta.startswith(self.ROOT_DIR):
                self.escribir(f"Error: No puedes leer archivos fuera de la carpeta raíz.")
                return
            if os.path.isfile(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.escribir(contenido)
            else:
                self.escribir(f"Archivo '{nombre}' no existe en el directorio actual.")
        except Exception as e:
            self.escribir(f"Error al leer archivo '{nombre}': {e}")

    def borrar_archivo(self, nombre):
        msg = self.fs.eliminar_archivo(nombre)
        self.escribir(msg)

    def listar_archivos(self):
        raiz = self.ROOT_DIR
        if not os.path.exists(raiz):
            self.escribir("Error: La carpeta raíz 'MiPC' no existe.")
            return

        def listar_recursivo(ruta, prefijo=""):
            try:
                elementos = sorted(os.listdir(ruta))
            except Exception as e:
                self.escribir(f"Error al acceder a {ruta}: {e}")
                return

            for elem in elementos:
                ruta_completa = os.path.join(ruta, elem)
                if os.path.isdir(ruta_completa):
                    self.escribir(f"{prefijo}[DIR]  {ruta_completa}")
                    listar_recursivo(ruta_completa, prefijo + "    ")
                else:
                    self.escribir(f"{prefijo}[FILE] {ruta_completa}")

        self.escribir(f"Contenido de {raiz}:")
        listar_recursivo(raiz)

    def crear_carpeta(self, nombre):
        msg = self.fs.crear_carpeta(nombre)
        self.escribir(msg)

    def mover_archivo(self, origen, destino):
        msg = self.fs.mover_archivo(origen, destino)
        self.escribir(msg)

    def cambiar_directorio(self, ruta):
        nueva_ruta = os.path.abspath(os.path.join(self.directorio_actual, ruta))

        # Controlar que no salga del directorio ROOT_DIR
        if not nueva_ruta.startswith(self.ROOT_DIR):
            self.escribir(f"Error: No puedes salir del directorio raíz '{self.ROOT_DIR}'")
            return

        if os.path.isdir(nueva_ruta):
            self.directorio_actual = nueva_ruta
            self.escribir(f"📂 Cambiado a: {self.directorio_actual}")
            self.listar_contenido_directorio()
        else:
            self.escribir(f"Error: El directorio '{ruta}' no existe.")

    # Cambiar también en listar_contenido_directorio si usa alguna ruta fija
    def listar_contenido_directorio(self):
        try:
            contenido = os.listdir(self.directorio_actual)
            if not contenido:
                self.escribir("📁 Carpeta vacía.")
                return

            carpetas = [f for f in contenido if os.path.isdir(os.path.join(self.directorio_actual, f))]
            archivos = [f for f in contenido if os.path.isfile(os.path.join(self.directorio_actual, f))]

            self.escribir("📂 Subcarpetas:")
            for c in carpetas:
                self.escribir(f"  [DIR]  {c}")

            self.escribir("📄 Archivos:")
            for a in archivos:
                self.escribir(f"  [FILE] {a}")

        except Exception as e:
            self.escribir(f"Error al listar contenido: {e}")

