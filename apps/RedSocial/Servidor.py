import os
import json
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, scrolledtext

PORT = 5000
DATA_DIR = "data"
FOROS_FILE = os.path.join(DATA_DIR, "foros.json")

HEADER_SIZE = 10
MAX_CONN = 10

def cargar_foros():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.isfile(FOROS_FILE):
        with open(FOROS_FILE, "w") as f:
            json.dump({}, f)
    with open(FOROS_FILE, "r") as f:
        return json.load(f)

def guardar_foros(foros):
    with open(FOROS_FILE, "w") as f:
        json.dump(foros, f, indent=2)

clientes = {}
def broadcast(canal, remitente, mensaje):
    for usuario, (sock, canal_actual) in clientes.items():
        if canal_actual == canal and usuario != remitente:
            try:
                sock.sendall(mensaje)
            except:
                pass

def manejar_cliente(sock, addr):
    nombre = sock.recv(50).decode().strip()
    canal = sock.recv(50).decode().strip()
    clientes[nombre] = (sock, canal)
    while True:
        try:
            header = sock.recv(HEADER_SIZE)
            if not header:
                break
            tam = int(sock.recv(HEADER_SIZE).decode())
            contenido = sock.recv(tam)
            broadcast(canal, nombre, header + f"{len(contenido):<{HEADER_SIZE}}".encode() + contenido)
        except:
            break
    del clientes[nombre]
    sock.close()

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen(MAX_CONN)
    print(f"[Servidor iniciado en el puerto {PORT}]")
    while True:
        sock, addr = server.accept()
        threading.Thread(target=manejar_cliente, args=(sock, addr), daemon=True).start()

class ClienteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Foro/Chat en Red")
        self.geometry("500x550")
        self.configure(bg="#d0d0d0")

        self.sock = None
        self.nombre = ""
        self.foro = ""
        self.canal = ""
        self.foros = cargar_foros()

        self.mensajes = scrolledtext.ScrolledText(self, state="disabled", wrap="word")
        self.mensajes.pack(padx=10, pady=10, fill="both", expand=True)

        self.entrada = tk.Entry(self)
        self.entrada.pack(fill="x", padx=10, pady=5)
        self.entrada.bind("<Return>", self.enviar_mensaje)

        self.btn_archivo = tk.Button(self, text="Enviar Archivo", command=self.enviar_archivo)
        self.btn_archivo.pack(pady=5)

        threading.Thread(target=self.iniciar_cliente, daemon=True).start()

    def seleccionar_opcion(self):
        modo = simpledialog.askstring("Modo", "¿Foro o Chat Directo? (foro/chat):")
        if modo not in ["foro", "chat"]:
            self.destroy()
            return
        self.nombre = simpledialog.askstring("Usuario", "Escribe tu nombre:")
        if modo == "foro":
            self.foro = simpledialog.askstring("Foro", f"Foros disponibles: {list(self.foros.keys())}\nEscribe nombre del foro o nuevo:")
            if self.foro not in self.foros:
                self.foros[self.foro] = []
            self.canal = simpledialog.askstring("Canal", f"Canales en '{self.foro}': {self.foros[self.foro]}\nEscribe canal o nuevo:")
            if self.canal not in self.foros[self.foro]:
                self.foros[self.foro].append(self.canal)
            guardar_foros(self.foros)
        else:
            self.canal = simpledialog.askstring("Chat", "Nombre del otro usuario para chat directo:")
            self.foro = "chat_directo"

    def iniciar_cliente(self):
        self.seleccionar_opcion()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(("localhost", PORT))
        except:
            messagebox.showerror("Error", "No se pudo conectar al servidor")
            self.destroy()
            return

        self.sock.sendall(f"{self.nombre:<50}".encode())
        self.sock.sendall(f"{self.canal:<50}".encode())
        threading.Thread(target=self.recibir_mensajes, daemon=True).start()

    def enviar_mensaje(self, event=None):
        msg = self.entrada.get().strip()
        if not msg: return
        msg_bytes = f"{self.nombre}: {msg}".encode()
        self.sock.sendall(b"MSG       " + f"{len(msg_bytes):<{HEADER_SIZE}}".encode() + msg_bytes)
        self.mostrar_mensaje(f"Tú: {msg}")
        self.entrada.delete(0, tk.END)

    def enviar_archivo(self):
        filepath = filedialog.askopenfilename()
        if not filepath: return
        nombre_archivo = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            data = f.read()
        contenido = f"{self.nombre}|{nombre_archivo}|".encode() + data
        self.sock.sendall(b"FILE      " + f"{len(contenido):<{HEADER_SIZE}}".encode() + contenido)
        self.mostrar_mensaje(f"Tú enviaste archivo: {nombre_archivo}")

    def recibir_mensajes(self):
        while True:
            try:
                header = self.sock.recv(HEADER_SIZE)
                if not header:
                    break
                tam = int(self.sock.recv(HEADER_SIZE).decode())
                contenido = self.sock.recv(tam)
                if header.strip() == b"MSG":
                    msg = contenido.decode()
                    self.mostrar_mensaje(msg)
                elif header.strip() == b"FILE":
                    parts = contenido.split(b"|", 2)
                    remitente = parts[0].decode()
                    nombre_archivo = parts[1].decode()
                    with open(f"recibido_{nombre_archivo}", "wb") as f:
                        f.write(parts[2])
                    self.mostrar_mensaje(f"{remitente} te envió un archivo: {nombre_archivo}")
            except:
                break

    def mostrar_mensaje(self, msg):
        self.mensajes.config(state="normal")
        self.mensajes.insert(tk.END, msg + "\n")
        self.mensajes.config(state="disabled")
        self.mensajes.yview(tk.END)

if __name__ == "__main__":
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    app = ClienteApp()
    app.mainloop()
