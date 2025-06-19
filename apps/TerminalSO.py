import tkinter as tk
import time
from kernel.Memoria import Memoria
from kernel.Planificador import Planificador
from kernel.SistemaDeArchivos import SistemaArchivos

class TerminalSO:
    def __init__(self, terminal_output, frame_terminal, boton_tarea, entrada):
        self.memoria = Memoria()
        self.procesos_activos = {}
        self.terminal_output = terminal_output
        self.frame_terminal = frame_terminal
        self.boton_tarea = boton_tarea
        self.entrada = entrada
        self.planificador = Planificador()
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
            "listar_archivos": self.listar_archivos
        }

        self.fs = SistemaArchivos() # File system

        self.argc = {
            "iniciar": 2,
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
            "listar_archivos": 0
        }

# relativos a la terminal
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
        self.escribir("  ayuda                  - Muestra esta ayuda")
        self.escribir("  iniciar <pid> <tam>    - Inicia un nuevo proceso")
        self.escribir("  terminar <pid>         - Termina un proceso")
        self.escribir("  listar                 - Lista todos los procesos")
        self.escribir("  memoria                - Muestra estado de la memoria")
        self.escribir("  limpiar                - Limpia la salida")
        self.escribir("  salir                  - Cierra esta terminal")
        self.escribir("  planificar_fifo        - Ejecuta el siguiente proceso FIFO")
        self.escribir("  planificar_rr          - Ejecuta el siguiente proceso Round Robin")
        self.escribir("  planificar_prioridad   - Ejecuta el siguiente proceso por prioridad")
        self.escribir("  crear_archivo <nombre> <contenido>  - Crea un archivo .txt con contenido")
        self.escribir("  leer_archivo <nombre>              - Muestra el contenido de un archivo")
        self.escribir("  borrar_archivo <nombre>            - Elimina un archivo")
        self.escribir("  listar_archivos                    - Muestra los archivos existentes")

    def limpiar_salida(self):
        try:
            self.terminal_output.config(state="normal")
            self.terminal_output.delete("1.0", tk.END)
            self.terminal_output.config(state="disabled")
        except tk.TclError:
            pass

    def cerrar_terminal(self, ventanas_abiertas):
        self.escribir("Cerrando terminal...")
        ventanas_abiertas.remove(self.frame_terminal)
        self.frame_terminal.destroy()
        self.boton_tarea.destroy()
        self.entrada.destroy()

    def ejecutar_comando_legacy_2(self, comando):
        partes = comando.strip().split()
        if not partes:
            return
        cmd = partes[0]
        args = partes[1:]
        print(args)
        if cmd in self.comandos:
            try:
                self.comandos[cmd](*args)
            except TypeError:
                self.escribir(f"Error: Número de argumentos incorrecto para '{cmd}'")
        else:
            self.escribir(f"Comando no reconocido: {cmd}. Escribe 'ayuda' para ver los comandos disponibles")

    def ejecutar_comando_legacy1(self, comando):
        partes = comando.strip().split()
        if not partes:
            return
        cmd = partes[0]
        args = partes[1:]
        print(f"[DEBUG] cmd: {cmd}, args: {args}")

        if cmd in self.comandos:
            esperado = self.argc.get(cmd, -1)
            if len(args) != esperado:
                self.escribir(f"Error: '{cmd}' espera {esperado} argumento(s), pero recibió {len(args)}.")
                return
            try:
                self.comandos[cmd](*args)
            except Exception as e:
                self.escribir(f"Error inesperado al ejecutar '{cmd}': {e}")
        else:
            self.escribir(f"Comando no reconocido: {cmd}. Escribe 'ayuda' para ver los comandos disponibles")

    def ejecutar_comando(self, comando):
        partes = comando.strip().split()
        if not partes:
            return

        cmd = partes[0]
        args = partes[1:]
        print(f"[DEBUG] cmd: {cmd}, args: {args}")

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

    # relativos a los procesos
    def iniciar_proceso(self, pid, tam):
        try:
            pid_int = int(pid)
            tam_int = int(tam)
            if pid_int in self.procesos_activos:
                self.escribir(f"Error: Ya existe un proceso con PID {pid_int}")
                return
            if self.memoria.asignar_memoria(pid_int, tam_int, None):
                self.procesos_activos[pid_int] = {
                    'tamanio': tam_int,
                    'inicio': time.time(),
                    'estado': 'Ejecutando',
                    'prioridad': pid_int % 5  # ejemplo prioridad
                }
                # Agregar proceso a planificadores
                proceso = {'pid': pid_int, 'prioridad': self.procesos_activos[pid_int]['prioridad']}
                self.planificador.agregar_proceso_fifo(proceso)
                self.planificador.agregar_proceso_rr(proceso)
                self.planificador.agregar_proceso_prioridad(proceso)

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
            tiempo = int(time.time() - info['inicio'])
            self.escribir(f"{pid}\t{info['tamanio']}\t{info['estado']}\t{tiempo}")

    def mostrar_memoria(self):
        self.escribir(str(self.memoria))

    # Métodos para planificador
    def planificar_fifo(self):
        resultado = self.planificador.ejecutar_fifo()
        self.escribir(resultado)

    def planificar_rr(self):
        resultado = self.planificador.ejecutar_rr(quantum=3)
        self.escribir(resultado)

    def planificar_prioridad(self):
        resultado = self.planificador.ejecutar_prioridad()
        self.escribir(resultado)


# relativos a los sistemas de archivos
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