import os
import json
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

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
    try:
        nombre = sock.recv(50).decode().strip()
        canal = sock.recv(50).decode().strip()
        clientes[nombre] = (sock, canal)
        while True:
            header = sock.recv(HEADER_SIZE)
            if not header:
                break
            tam = int(sock.recv(HEADER_SIZE).decode())
            contenido = sock.recv(tam)
            broadcast(canal, nombre, header + f"{len(contenido):<{HEADER_SIZE}}".encode() + contenido)
    except:
        pass
    finally:
        if nombre in clientes:
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
        self.title("Red Social Local")
        self.geometry("600x650")
        self.configure(bg="#f0f0f0")

        self.sock = None
        self.nombre = ""
        self.foro = ""
        self.canal = ""
        self.ip_servidor = ""
        self.foros = cargar_foros()

        self.contenedor_login = tk.Frame(self, bg="#f0f0f0")
        self.contenedor_login.pack(pady=20)

        tk.Label(self.contenedor_login, text="Tu nombre:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = tk.Entry(self.contenedor_login)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.contenedor_login, text="IP del servidor:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5)
        self.entry_ip = tk.Entry(self.contenedor_login)
        self.entry_ip.insert(0, "127.0.0.1")  # valor por defecto localhost
        self.entry_ip.grid(row=1, column=1, padx=5, pady=5)

        self.btn_foro = tk.Button(self.contenedor_login, text="Entrar a Foro", command=self.seleccionar_foro)
        self.btn_chat = tk.Button(self.contenedor_login, text="Chat Directo", command=self.seleccionar_chat)
        self.btn_foro.grid(row=2, column=0, padx=5, pady=10)
        self.btn_chat.grid(row=2, column=1, padx=5, pady=10)

        self.chat_frame = None

    def seleccionar_foro(self):
        self.nombre = self.entry_nombre.get().strip()
        self.ip_servidor = self.entry_ip.get().strip()
        if not self.nombre:
            messagebox.showerror("Error", "Debes ingresar tu nombre")
            return
        if not self.ip_servidor:
            messagebox.showerror("Error", "Debes ingresar la IP del servidor")
            return
        ventana_foro = tk.Toplevel(self)
        ventana_foro.title("Foros y Canales")
        tk.Label(ventana_foro, text="Selecciona o crea un foro:").pack()
        lista_foros = ttk.Combobox(ventana_foro, values=list(self.foros.keys()))
        lista_foros.pack(pady=5)
        entry_foro = tk.Entry(ventana_foro)
        entry_foro.pack(pady=5)
        tk.Label(ventana_foro, text="Canal dentro del foro:").pack()
        entry_canal = tk.Entry(ventana_foro)
        entry_canal.pack(pady=5)
        def continuar():
            foro = entry_foro.get() or lista_foros.get()
            canal = entry_canal.get()
            if not foro or not canal:
                messagebox.showerror("Error", "Completa foro y canal")
                return
            if foro not in self.foros:
                self.foros[foro] = []
            if canal not in self.foros[foro]:
                self.foros[foro].append(canal)
            guardar_foros(self.foros)
            self.foro = foro
            self.canal = canal
            ventana_foro.destroy()
            self.contenedor_login.destroy()
            self.iniciar_cliente()
        tk.Button(ventana_foro, text="Entrar", command=continuar).pack(pady=10)

    def seleccionar_chat(self):
        self.nombre = self.entry_nombre.get().strip()
        self.ip_servidor = self.entry_ip.get().strip()
        if not self.nombre:
            messagebox.showerror("Error", "Debes ingresar tu nombre")
            return
        if not self.ip_servidor:
            messagebox.showerror("Error", "Debes ingresar la IP del servidor")
            return
        ventana_chat = tk.Toplevel(self)
        ventana_chat.title("Chat directo")
        tk.Label(ventana_chat, text="Nombre del otro usuario:").pack()
        entry = tk.Entry(ventana_chat)
        entry.pack(pady=10)
        def continuar():
            otro = entry.get().strip()
            if not otro:
                return
            self.foro = "chat_directo"
            self.canal = otro
            ventana_chat.destroy()
            self.contenedor_login.destroy()
            self.iniciar_cliente()
        tk.Button(ventana_chat, text="Conectar", command=continuar).pack()

    def iniciar_cliente(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip_servidor, PORT))
        except:
            messagebox.showerror("Error", f"No se pudo conectar al servidor en {self.ip_servidor}:{PORT}")
            self.destroy()
            return
        self.sock.sendall(f"{self.nombre:<50}".encode())
        self.sock.sendall(f"{self.canal:<50}".encode())
        self.mostrar_chat()
        threading.Thread(target=self.recibir_mensajes, daemon=True).start()

    def mostrar_chat(self):
        self.chat_frame = tk.Frame(self, bg="#ffffff")
        self.chat_frame.pack(fill="both", expand=True)

        self.mensajes = scrolledtext.ScrolledText(self.chat_frame, state="disabled", wrap="word", bg="#fefefe")
        self.mensajes.pack(padx=10, pady=10, fill="both", expand=True)

        entry_frame = tk.Frame(self.chat_frame)
        entry_frame.pack(fill="x", padx=10, pady=5)

        self.entrada = tk.Entry(entry_frame)
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.bind("<Return>", self.enviar_mensaje)

        btn_send = tk.Button(entry_frame, text="Enviar", command=self.enviar_mensaje)
        btn_send.pack(side="left", padx=5)

        btn_archivo = tk.Button(self.chat_frame, text="Enviar Archivo", command=self.enviar_archivo)
        btn_archivo.pack(pady=5)

    def enviar_mensaje(self, event=None):
        msg = self.entrada.get().strip()
        if not msg:
            return
        msg_bytes = f"{self.nombre}: {msg}".encode()
        self.sock.sendall(b"MSG       " + f"{len(msg_bytes):<{HEADER_SIZE}}".encode() + msg_bytes)
        self.mostrar_mensaje(f"Tú: {msg}")
        self.entrada.delete(0, tk.END)

    def enviar_archivo(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
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
