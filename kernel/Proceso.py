import time
from threading import Thread

# 🧠 Gestor de PIDs
class GestorPID:
    siguiente_pid = 1

    @classmethod
    def obtener_pid(cls):
        pid = cls.siguiente_pid
        cls.siguiente_pid += 1
        return pid

# 🧵 Proceso como hilo que ejecuta una función simulada
class Proceso(Thread):
    def __init__(self, inicio, tamanio, func, pid):
        super().__init__()
        self.inicio = inicio
        self.tamanio = tamanio
        self.pid = pid
        self.func = func


    def run(self):
        if self.func:
            self.func(self.inicio, self.tamanio)
        else:
            print(f"[Proceso {self.pid}] No se asignó ninguna función.")

def tarea_ejemplo(inicio, tamanio):
    for i in range(5):
        print(f"[Proceso simulado] PID ocupando {tamanio} bloques desde {inicio}... ({i + 1}/5)")
        time.sleep(1)

def holamundo(inicio = None, tamanio= None):
    print("holamundo")
    time.sleep(1)

if __name__ == "__main__":
    proceso = Proceso(10, 5, tarea_ejemplo)
    proceso.start()
    proceso.join()  # Espera a que termine
