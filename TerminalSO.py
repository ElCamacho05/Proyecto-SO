# TerminalSO.py

import tkinter as tk
import time
from Memoria import Memoria

class TerminalSO:
    def __init__(self, terminal_output, frame_terminal, boton_tarea, entrada):
        self.memoria = Memoria()
        self.procesos_activos = {}
        self.terminal_output = terminal_output
        self.frame_terminal = frame_terminal
        self.boton_tarea = boton_tarea
        self.entrada = entrada
        self.comandos = {
            "ayuda": self.mostrar_ayuda,
            "iniciar": self.iniciar_proceso,
            "terminar": self.terminar_proceso,
            "listar": self.listar_procesos,
            "memoria": self.mostrar_memoria,
            "limpiar": self.limpiar_salida,
            "salir": self.cerrar_terminal
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
        self.escribir("Comandos disponibles:")
        self.escribir("  ayuda               - Muestra esta ayuda")
        self.escribir("  iniciar <pid> <tam> - Inicia un nuevo proceso")
        self.escribir("  terminar <pid>      - Termina un proceso")
        self.escribir("  listar              - Lista todos los procesos")
        self.escribir("  memoria             - Muestra estado de la memoria")
        self.escribir("  limpiar             - Limpia la salida")
        self.escribir("  salir               - Cierra esta terminal")

    def iniciar_proceso(self, pid, tam):
        try:
            pid_int = int(pid)
            tam_int = int(tam)
            if pid_int in self.procesos_activos:
                self.escribir(f"Error: Ya existe un proceso con PID {pid_int}")
                return
            if self.memoria.asignar_memoria(pid_int, tam_int):
                self.procesos_activos[pid_int] = {
                    'tamanio': tam_int,
                    'inicio': time.time(),
                    'estado': 'Ejecutando'
                }
                self.escribir(f"Proceso {pid_int} iniciado correctamente")
            else:
                self.escribir("Error: No se pudo asignar memoria")
        except ValueError:
            self.escribir("Error: PID y tamaño deben ser números enteros")

    def terminar_proceso(self, pid):
        try:
            pid_int = int(pid)
            if pid_int not in self.procesos_activos:
                self.escribir(f"Error: No existe un proceso con PID {pid_int}")
                return
            self.memoria.liberar_memoria(pid_int)
            del self.procesos_activos[pid_int]
            self.escribir(f"Proceso {pid_int} terminado correctamente")
        except ValueError:
            self.escribir("Error: PID debe ser un número entero")

    def listar_procesos(self):
        if not self.procesos_activos:
            self.escribir("No hay procesos activos")
            return
        self.escribir("PID\tTamaño\tEstado\t\tTiempo (s)")
        for pid, info in self.procesos_activos.items():
            tiempo_ejecucion = int(time.time() - info['inicio'])
            self.escribir(f"{pid}\t{info['tamanio']}\t{info['estado']}\t{tiempo_ejecucion}")

    def mostrar_memoria(self):
        self.escribir(str(self.memoria))

    def limpiar_salida(self):
        try:
            self.terminal_output.config(state="normal")
            self.terminal_output.delete("1.0", tk.END)
            self.terminal_output.config(state="disabled")
        except tk.TclError:
            pass

    def cerrar_terminal(self):
        self.escribir("Cerrando terminal...")
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
            try:
                self.comandos[cmd](*args)
            except TypeError:
                self.escribir(f"Error: Número de argumentos incorrecto para '{cmd}'")
        else:
            self.escribir(f"Comando no reconocido: {cmd}. Escribe 'ayuda' para ver los comandos disponibles")
