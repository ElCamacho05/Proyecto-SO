from Proceso import Proceso


class Memoria:
    def __init__(self, tamanio=100):
        self.tamanio = tamanio
        self.memoria = [0] * self.tamanio
        self.procesos = []  # [(pid, inicio), (pid, inicio)...]

    def asignar_memoria(self, pid, tamanio, func):

        libres = 0
        inicio = -1

        for i in range(len(self.memoria)):  # si esta libre lo asigna desde el espacio
            if self.memoria[i] == 0:
                if libres == 0:
                    inicio = i
                libres += 1
                if libres == tamanio:
                    for j in range(inicio, inicio + tamanio):
                        self.memoria[j] = pid
                    proceso = Proceso(inicio, tamanio, pid, func)
                    self.procesos.append(proceso)
                    print(f"Memoria asignada al proceso {pid} desde {inicio} hasta {inicio + tamanio - 1}")
                    return True
            else:
                libres = 0

        print("No hay suficiente memoria contigua disponible.")
        return False

    def liberar_memoria(self, pid):
        liberados = 0
        for i in range(len(self.memoria)):
            if self.memoria[i] == pid:
                self.memoria[i] = 0
                liberados += 1
        for i, p in enumerate(self.procesos):
            if p.pid == pid:
                self.procesos.pop(i)
        print(f"Se liberaron {liberados} bloques del proceso {pid}.")

    def __str__(self):
        print("Estado de la memoria:")
        s = ""
        for i in range(0, self.tamanio, 20):  # Mostrar por filas de 20
            fila = self.memoria[i:i + 20]
            s += " ".join([str(b) if b != 0 else "-" for b in fila])
            s += "\n"
        s += "Procesos:\n"
        for p in self.procesos:
            s += f"Pid: {p.pid}, Inicio: {p.inicio}\n"
        return s


def main():
    mem = Memoria()
    mem.asignar_memoria(1, 10, None)
    mem.asignar_memoria(2, 15, None)
    print(mem)
    mem.liberar_memoria(1)
    print(mem)
    mem.asignar_memoria(3, 8, None)
    print(mem)
    mem.asignar_memoria(4, 4, None)
    print(mem)

    mem.asignar_memoria(5, 1, holamundo())
    mem.procesos[-1].run()


def holamundo():
    print("holamundo")

if __name__ == "__main__":
    main()
