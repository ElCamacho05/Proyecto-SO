import random
import tkinter as tk
import time

from kernel.Memoria import Memoria
from kernel.Planificador import Planificador
from kernel.SistemaDeArchivos import SistemaArchivos
from kernel.Proceso import GestorPID
from gui.data.funciones import funciones_disponibles

class TerminalSO:
    def __init__(self, terminal_output, frame_terminal, boton_tarea, entrada, ventanas_abiertas, procesos_activos=None, planificador=None):
        self.memoria = Memoria()
        self.procesos_activos = procesos_activos if procesos_activos is not None else {}

        self.terminal_output = terminal_output
        self.frame_terminal = frame_terminal
        self.boton_tarea = boton_tarea
        self.entrada = entrada
        self.planificador = Planificador() if not planificador else planificador
        self.ventanas_abiertas = ventanas_abiertas
        self.fs = SistemaArchivos()

        self.comandos = {
            "ayuda": self.mostrar_ayuda,
            "iniciar": self.iniciar_proceso,
            "terminar": self.terminar_proceso,
            "listar": self.listar_procesos,
            "memoria": self.mostrar_memoria,
            "limpiar": self.limpiar_salida,
            "salir": self.cerrar_terminal,
            "planificar_fifo": self.planificar_fifo,
            "planificar_rr": self.planificar_rr,
            "planificar_prioridad": self.planificar_prioridad,
            "crear_archivo": self.crear_archivo,
            "leer_archivo": self.leer_archivo,
            "borrar_archivo": self.borrar_archivo,
            "listar_archivos": self.listar_archivos,
            "crear_carpeta": self.crear_carpeta,
            "mover_archivo": self.mover_archivo
        }

        self.argc = {
            "iniciar": -1,
            "terminar": 1,
            "listar": 0,
            "memoria": 0,
            "limpiar": 0,
            "salir": 0,
            "ayuda": 0,
            "planificar_fifo": 0,
            "planificar_rr": 0,
            "planificar_prioridad": 0,
            "crear_archivo": -1,
            "leer_archivo": 1,
            "borrar_archivo": 1,
            "listar_archivos": 0,
            "crear_carpeta": 1,
            "mover_archivo": 2
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
            "iniciar <func/None> - Inicia un nuevo proceso",
            "terminar <pid> - Termina un proceso",
            "listar - Lista todos los procesos",
            "memoria - Muestra estado de la memoria",
            "limpiar - Limpia la salida",
            "salir - Cierra esta terminal",
            "planificar_fifo - Ejecuta el siguiente proceso FIFO",
            "planificar_rr - Ejecuta el siguiente proceso Round Robin",
            "planificar_prioridad - Ejecuta el siguiente proceso por prioridad",
            "crear_archivo <nombre> <contenido> - Crea un archivo .txt",
            "leer_archivo <nombre> - Muestra el contenido de un archivo",
            "borrar_archivo <nombre> - Elimina un archivo",
            "listar_archivos - Muestra los archivos existentes",
            "crear_carpeta - Crea una carpeta en el directorio especificado.",
            "mover_archivo <origin/dest> - mueve un archivo a una ubicacion deseada"
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
        msg = self.fs.leer_archivo(nombre)
        self.escribir(msg)

    def borrar_archivo(self, nombre):
        msg = self.fs.eliminar_archivo(nombre)
        self.escribir(msg)

    def listar_archivos(self):
        archivos = self.fs.listar_archivos()
        if archivos:
            for a in archivos:
                self.escribir(f" - {a}")
        else:
            self.escribir("No hay archivos en el sistema.")

    def crear_carpeta(self, nombre):
        msg = self.fs.crear_carpeta(nombre)
        self.escribir(msg)

    def mover_archivo(self, origen, destino):
        msg = self.fs.mover_archivo(origen, destino)
        self.escribir(msg)