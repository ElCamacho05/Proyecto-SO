from threading import Thread


class Proceso(Thread):
    def __init__(self, inicio, tamanio, pid, func):
        self.inicio = inicio
        self.tamanio = tamanio
        self.pid = pid

        self.proceso = Thread(target=func, args=(self.inicio, self.tamanio))


    def run(self):
        self.proceso.start()

