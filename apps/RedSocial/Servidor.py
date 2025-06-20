import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json

PORT = 5000
DATA_DIR = "data"
FOROS_FILE = os.path.join(DATA_DIR, "foros.json")
HEADER_SIZE = 10

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

class ForoChatApp:
    def __init__(self, contenedor, servidor_ip="127.0.0.1"):
        self.frame = tk.Frame(contenedor, bg="#e0e0e0")
        self.frame.pack(fill="both", expand=True)

        self.sock = None
        self.nombre = ""
        self.foro = ""
        self.canal = ""
        self.ip_servidor = servidor_ip
        self.foros = cargar_foros()
        self.feedbackColors = ['gray'] * 5

        self.build_login()

    def build_login(self):
        login = tk.Frame(self.frame, bg="#e0e0e0")
        login.pack(pady=15)

        tk.Label(login, text="Tu nombre:", bg="#e0e0e0").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = tk.Entry(login)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(login, text="IP del servidor:", bg="#e0e0e0").grid(row=1, column=0, padx=5, pady=5)
        self.entry_ip = tk.Entry(login)
        self.entry_ip.insert(0, self.ip_servidor)
        self.entry_ip.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(login, text="Foro", command=self.seleccionar_foro).grid(row=2, column=0, pady=8)
        tk.Button(login, text="Chat Directo", command=self.seleccionar_chat).grid(row=2, column=1, pady=8)

    def seleccionar_foro(self):
        self.nombre = self.entry_nombre.get().strip()
        self.ip_servidor = self.entry_ip.get().strip()
        if not self.nombre or not self.ip_servidor:
            messagebox.showerror("Error", "Completa nombre y IP")
            return
        ventana_foro = tk.Toplevel(self.frame)
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
            self.iniciar_cliente()

        tk.Button(ventana_foro, text="Entrar", command=continuar).pack(pady=10)

    def seleccionar_chat(self):
        self.nombre = self.entry_nombre.get().strip()
        self.ip_servidor = self.entry_ip.get().strip()
        if not self.nombre or not self.ip_servidor:
            messagebox.showerror("Error", "Completa nombre y IP")
            return
        ventana_chat = tk.Toplevel(self.frame)
        ventana_chat.title("Chat directo")
        tk.Label(ventana_chat, text="Nombre del otro usuario:").pack()
        entry = tk.Entry(ventana_chat)
        entry.pack(pady=5)

        def continuar():
            otro = entry.get().strip()
            if not otro:
                return
            self.foro = "chat_directo"
            self.canal = otro
            ventana_chat.destroy()
            self.iniciar_cliente()

        tk.Button(ventana_chat, text="Conectar", command=continuar).pack()

    def iniciar_cliente(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip_servidor, PORT))
        except:
            messagebox.showerror("Error", f"No se pudo conectar al servidor en {self.ip_servidor}:{PORT}")
            self.frame.destroy()
            return
        self.sock.sendall(f"{self.nombre:<50}".encode())
        self.sock.sendall(f"{self.canal:<50}".encode())
        self.mostrar_chat()
        threading.Thread(target=self.recibir_mensajes, daemon=True).start()

    def mostrar_chat(self):
        self.frame.pack_forget()
        chat = tk.Frame(self.frame, bg="white")
        chat.pack(fill="both", expand=True)

        self.mensajes = scrolledtext.ScrolledText(chat, state="disabled", wrap="word", bg="#fefefe", font=("Courier", 10))
        self.mensajes.pack(padx=10, pady=10, fill="both", expand=True)

        entry_frame = tk.Frame(chat)
        entry_frame.pack(fill="x", padx=10, pady=5)
        self.entrada = tk.Entry(entry_frame)
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.bind("<Return>", self.enviar_mensaje)

        tk.Button(entry_frame, text="Enviar", command=self.enviar_mensaje).pack(side="left", padx=5)
        tk.Button(chat, text="Enviar Archivo", command=self.enviar_archivo).pack(pady=5)

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
                    self.mostrar_mensaje(contenido.decode())
                elif header.strip() == b"FILE":
                    remitente, nombre_archivo, archivo = contenido.split(b"|", 2)
                    with open(f"recibido_{nombre_archivo.decode()}", "wb") as f:
                        f.write(archivo)
                    self.mostrar_mensaje(f"{remitente.decode()} te envió un archivo: {nombre_archivo.decode()}")
            except:
                break

    def mostrar_mensaje(self, msg):
        self.mensajes.config(state="normal")
        self.mensajes.insert(tk.END, msg + "\n")
        self.mensajes.config(state="disabled")
        self.mensajes.yview(tk.END)
