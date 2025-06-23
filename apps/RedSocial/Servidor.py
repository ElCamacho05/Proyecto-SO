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
        self.frame = tk.Frame(contenedor, bg="white")
        self.frame.pack(fill="both", expand=True)

        self.sock = None
        self.nombre = ""
        self.foro = "ForoGlobal"
        self.canal = ""
        self.ip_servidor = servidor_ip
        self.foros = cargar_foros()
        self.canales_actuales = []
        self.canal_seleccionado = tk.StringVar()

        self.armar_interfaz()

    def armar_interfaz(self):
        top = tk.Frame(self.frame, bg="#2c2f33")
        top.pack(fill="x")

        tk.Label(top, text="Nombre:", bg="#2c2f33", fg="white").pack(side="left", padx=5)
        self.entry_nombre = tk.Entry(top)
        self.entry_nombre.pack(side="left", padx=5)

        tk.Label(top, text="IP:", bg="#2c2f33", fg="white").pack(side="left")
        self.entry_ip = tk.Entry(top)
        self.entry_ip.insert(0, self.ip_servidor)
        self.entry_ip.pack(side="left", padx=5)

        tk.Button(top, text="🚀 Conectar", command=self.conectar,
                  font=("Arial", 10, "bold"), bg="#7289da", fg="white",
                  height=2, width=12).pack(side="left", padx=10, pady=5)

        cuerpo = tk.Frame(self.frame)
        cuerpo.pack(fill="both", expand=True)

        # Panel izquierdo: canales
        self.panel_izquierdo = tk.Frame(cuerpo, bg="#23272a", width=200)
        self.panel_izquierdo.pack(side="left", fill="y")

        tk.Label(self.panel_izquierdo, text="Canales", bg="#23272a", fg="white", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Button(self.panel_izquierdo, text="📖 Tutorial", command=self.mostrar_tutorial,
                  bg="#23272a", fg="white", activebackground="#99aab5", activeforeground="white",
                  bd=0, anchor="w").pack(fill="x", padx=5, pady=2)

        self.lista_canales = tk.Listbox(self.panel_izquierdo, bg="#2c2f33", fg="white")
        self.lista_canales.pack(fill="both", expand=True, padx=5)
        self.lista_canales.bind("<<ListboxSelect>>", self.seleccionar_canal)

        tk.Button(self.panel_izquierdo, text="+ Añadir canal", command=self.agregar_canal).pack(pady=5)

        # Panel derecho: chat
        self.panel_derecho = tk.Frame(cuerpo, bg="white")
        self.panel_derecho.pack(side="left", fill="both", expand=True)

        self.label_canal = tk.Label(self.panel_derecho, text="Canal: Ninguno", bg="white", font=("Arial", 12, "bold"))
        self.label_canal.pack(anchor="w", padx=10, pady=5)

        self.mensajes = scrolledtext.ScrolledText(self.panel_derecho, state="disabled", wrap="word", bg="#fefefe", font=("Courier", 10))
        self.mensajes.pack(padx=10, pady=5, fill="both", expand=True)

        entry_frame = tk.Frame(self.panel_derecho, bg="white")
        entry_frame.pack(fill="x", padx=10, pady=5)

        self.entrada = tk.Entry(entry_frame)
        self.entrada.pack(side="left", fill="x", expand=True)
        self.entrada.bind("<Return>", self.enviar_mensaje)

        tk.Button(entry_frame, text="Enviar", command=self.enviar_mensaje).pack(side="left", padx=5)
        tk.Button(entry_frame, text="Archivo", command=self.enviar_archivo).pack(side="left")

    def conectar(self):
        self.nombre = self.entry_nombre.get().strip()
        self.ip_servidor = self.entry_ip.get().strip()
        if not self.nombre or not self.ip_servidor:
            messagebox.showerror("Error", "Completa tu nombre y la IP del servidor.")
            return

        self.foros = cargar_foros()
        self.foros.setdefault(self.foro, ["general"])
        guardar_foros(self.foros)

        self.canales_actuales = self.foros[self.foro]
        self.actualizar_lista_canales()
        self.seleccionar_canal_por_nombre("general")

    def actualizar_lista_canales(self):
        self.lista_canales.delete(0, tk.END)
        for canal in self.canales_actuales:
            self.lista_canales.insert(tk.END, canal)

    def seleccionar_canal(self, event):
        seleccion = self.lista_canales.curselection()
        if seleccion:
            canal = self.lista_canales.get(seleccion[0])
            self.seleccionar_canal_por_nombre(canal)

    def seleccionar_canal_por_nombre(self, canal):
        self.canal = canal
        self.label_canal.config(text=f"Canal: #{canal}")
        self.iniciar_cliente()

    def agregar_canal(self):
        nuevo = tk.simpledialog.askstring("Nuevo canal", "Nombre del nuevo canal:")
        if nuevo and nuevo not in self.canales_actuales:
            self.canales_actuales.append(nuevo)
            guardar_foros(self.foros)
            self.actualizar_lista_canales()

    def iniciar_cliente(self):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip_servidor, PORT))
        except:
            messagebox.showerror("Error", f"No se pudo conectar al servidor en {self.ip_servidor}:{PORT}")
            return
        self.sock.sendall(f"{self.nombre:<50}".encode())
        self.sock.sendall(f"{self.canal:<50}".encode())
        self.mensajes.config(state="normal")
        self.mensajes.delete("1.0", tk.END)
        self.mensajes.config(state="disabled")
        threading.Thread(target=self.recibir_mensajes, daemon=True).start()

    def mostrar_mensaje(self, msg):
        self.mensajes.config(state="normal")
        self.mensajes.insert(tk.END, msg + "\n")
        self.mensajes.config(state="disabled")
        self.mensajes.yview(tk.END)

    def mostrar_tutorial(self):
        self.label_canal.config(text="📖 Tutorial")
        self.mensajes.config(state="normal")
        self.mensajes.delete("1.0", tk.END)

        texto = (
            "👋 ¡Bienvenido al Chat Tapioka!\n\n"
            "👉 PASOS PARA USAR:\n"
            "1. Escribe tu nombre en la parte superior.\n"
            "2. Escribe la IP del servidor o usa la predeterminada (127.0.0.1).\n"
            "3. Haz clic en 'Conectar'.\n"
            "4. A la izquierda verás los canales disponibles. Haz clic en uno para unirte.\n"
            "5. Usa la caja de texto abajo para enviar mensajes.\n"
            "6. Usa el botón 'Archivo' para compartir archivos.\n\n"
            "✅ Puedes crear tus propios canales con '+ Añadir canal'.\n"
            "✅ Todo se guarda automáticamente.\n\n"
            "🎨 Consejo: Si algo no se conecta, revisa que el servidor esté corriendo.\n"
        )

        self.mensajes.insert(tk.END, texto)
        self.mensajes.config(state="disabled")

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
                    self.mostrar_mensaje(f"{remitente.decode()} te envió archivo: {nombre_archivo.decode()}")
            except:
                break


    def mostrar_mensaje(self, msg):
        self.mensajes.config(state="normal")
        self.mensajes.insert(tk.END, msg + "\n")
        self.mensajes.config(state="disabled")
        self.mensajes.yview(tk.END)
