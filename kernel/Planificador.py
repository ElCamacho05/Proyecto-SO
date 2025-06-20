from collections import deque

class Planificador:
    _instancia = None  # Atributo de clase para guardar la instancia única

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super(Planificador, cls).__new__(cls)
            # Inicialización solo una vez
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.cola_fifo = deque()
        self.cola_round_robin = deque()
        self.cola_prioridad = []

    def agregar_proceso_fifo(self, proceso):
        self.cola_fifo.append(proceso)

    def ejecutar_fifo(self):
        if self.cola_fifo:
            proceso = self.cola_fifo.popleft()
            return f"Ejecutando FIFO: Proceso PID {proceso['pid']}", proceso['pid']
        return "FIFO: No hay procesos en espera"

    def agregar_proceso_rr(self, proceso):
        self.cola_round_robin.append(proceso)

    def ejecutar_rr(self, quantum):
        if not self.cola_round_robin:
            return "RR: No hay procesos"
        proceso = self.cola_round_robin.popleft()
        self.cola_round_robin.append(proceso)
        return f"Round Robin ejecuta PID {proceso['pid']} con quantum {quantum}", proceso['pid']

    def agregar_proceso_prioridad(self, proceso):
        self.cola_prioridad.append(proceso)
        self.cola_prioridad.sort(key=lambda p: p['prioridad'])

    def ejecutar_prioridad(self):
        if self.cola_prioridad:
            proceso = self.cola_prioridad.pop(0)
            return f"Ejecutando por prioridad: PID {proceso['pid']}", proceso['pid']
        return "Prioridad: No hay procesos"

    def eliminar_proceso(self, pid):
        # FIFO
        self.cola_fifo = deque([p for p in self.cola_fifo if p['pid'] != pid])

        # Round Robin
        self.cola_round_robin = deque([p for p in self.cola_round_robin if p['pid'] != pid])

        # Prioridad (es una lista normal)
        self.cola_prioridad = [p for p in self.cola_prioridad if p['pid'] != pid]
