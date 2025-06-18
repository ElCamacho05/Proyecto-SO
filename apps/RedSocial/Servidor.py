import socket
import threading
import os
import tkinter as tk
from tkinter import simpledialog, filedialog, scrolledtext, messagebox
import queue
import time

HEADER_SIZE = 10
FILE_HEADER_SIZE = 20
PORT = 5555

def recvall(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def prepare_msg_packet(msg):
    packet = b'MSG       '
    msg_bytes = msg.encode()
    packet += f"{len(msg_bytes):<{HEADER_SIZE}}".encode()
    packet += msg_bytes
    return packet

def prepare_file_packet(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    packet = b'FILE      '
    packet += f"{len(filename):<{HEADER_SIZE}}".encode()
    packet += filename.encode()
    packet += f"{filesize:<{FILE_HEADER_SIZE}}".encode()

    return packet, filesize

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Messenger 2000 Simulado")
        self.geometry("400x500")
        self.configure(bg="#c0c0c0")  # Gris clásico
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.sock = None
        self.running = False

        self.send_queue = queue.Queue()

        self.create_widgets()
        self.ask_mode()

    def create_widgets(self):
        self.chat_area = scrolledtext.ScrolledText(self, bg="white", fg="black", font=("MS Sans Serif", 10), state='disabled')
        self.chat_area.place(x=10, y=10, width=380, height=380)

        self.entry_text = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.entry_text, font=("MS Sans Serif", 10))
        self.entry.place(x=10, y=400, width=300, height=25)
        self.entry.bind("<Return>", self.enqueue_message)

        self.send_btn = tk.Button(self, text="Enviar", font=("MS Sans Serif", 9, "bold"), command=self.enqueue_message)
        self.send_btn.place(x=320, y=400, width=70, height=25)

        self.file_btn = tk.Button(self, text="Enviar Archivo", font=("MS Sans Serif", 8), command=self.enqueue_file)
        self.file_btn.place(x=10, y=435, width=380, height=30)

        self.status_label = tk.Label(self, text="No conectado", bg="#c0c0c0", fg="black", font=("MS Sans Serif", 8))
        self.status_label.place(x=10, y=475)

    def ask_mode(self):
        mode = simpledialog.askstring("Modo", "Ingrese modo:\n's' para servidor\n'c' para cliente", parent=self)
        if mode is None:
            self.destroy()
            return

        mode = mode.lower()
        if mode == 's':
            threading.Thread(target=self.start_server, daemon=True).start()
        elif mode == 'c':
            ip = simpledialog.askstring("IP Servidor", "Ingrese la IP del servidor:", parent=self)
            if ip:
                threading.Thread(target=self.start_client, args=(ip,), daemon=True).start()
            else:
                self.destroy()
        else:
            messagebox.showerror("Error", "Modo inválido")
            self.destroy()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", PORT))
        server.listen(1)
        self.update_status("Esperando conexión...")
        conn, addr = server.accept()
        self.sock = conn
        self.update_status(f"Conectado a {addr}")
        self.running = True
        threading.Thread(target=self.handle_receive, daemon=True).start()
        threading.Thread(target=self.handle_send, daemon=True).start()

    def start_client(self, ip):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((ip, PORT))
            self.sock = client
            self.update_status(f"Conectado a {ip}:{PORT}")
            self.running = True
            threading.Thread(target=self.handle_receive, daemon=True).start()
            threading.Thread(target=self.handle_send, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar: {e}")
            self.destroy()

    def handle_receive(self):
        while self.running:
            try:
                header = recvall(self.sock, HEADER_SIZE)
                if not header:
                    self.update_status("Conexión cerrada.")
                    break

                header = header.decode().strip()
                if header == 'MSG':
                    length_bytes = recvall(self.sock, HEADER_SIZE)
                    if not length_bytes:
                        break
                    length = int(length_bytes.decode().strip())
                    msg_bytes = recvall(self.sock, length)
                    if not msg_bytes:
                        break
                    msg = msg_bytes.decode()
                    self.append_message(msg, "left")

                elif header == 'FILE':
                    filename_len_bytes = recvall(self.sock, HEADER_SIZE)
                    if not filename_len_bytes:
                        break
                    filename_len = int(filename_len_bytes.decode().strip())
                    filename_bytes = recvall(self.sock, filename_len)
                    if not filename_bytes:
                        break
                    filename = filename_bytes.decode()

                    filesize_bytes = recvall(self.sock, FILE_HEADER_SIZE)
                    if not filesize_bytes:
                        break
                    filesize = int(filesize_bytes.decode().strip())

                    with open(f"recibido_{filename}", "wb") as f:
                        bytes_received = 0
                        while bytes_received < filesize:
                            chunk = self.sock.recv(min(4096, filesize - bytes_received))
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    self.append_message(f"[Archivo recibido]: recibido_{filename}", "left")

                else:
                    self.append_message(f"[Error] Cabecera desconocida: {header}", "left")

            except Exception as e:
                self.append_message(f"[Error al recibir]: {e}", "left")
                break

        self.running = False
        try:
            self.sock.close()
        except:
            pass
        self.update_status("Desconectado")

    def handle_send(self):
        while self.running:
            try:
                item = self.send_queue.get()
                if item is None:
                    break  # Señal para cerrar hilo

                tipo, contenido = item

                if tipo == 'msg':
                    packet = prepare_msg_packet(contenido)
                    self.sock.sendall(packet)

                elif tipo == 'file':
                    filepath = contenido
                    packet, filesize = prepare_file_packet(filepath)
                    self.sock.sendall(packet)
                    with open(filepath, "rb") as f:
                        while True:
                            bytes_read = f.read(4096)
                            if not bytes_read:
                                break
                            self.sock.sendall(bytes_read)

                self.send_queue.task_done()
            except Exception as e:
                self.append_message(f"[Error al enviar]: {e}", "right")
                break

    def append_message(self, msg, side):
        self.chat_area.config(state='normal')
        if side == "left":
            self.chat_area.insert(tk.END, f"Amigo: {msg}\n", ("left",))
        else:
            self.chat_area.insert(tk.END, f"Tú: {msg}\n", ("right",))
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def enqueue_message(self, event=None):
        msg = self.entry_text.get().strip()
        if not msg or not self.running:
            return
        self.send_queue.put(('msg', msg))
        self.append_message(msg, "right")
        self.entry_text.set("")

    def enqueue_file(self):
        if not self.running:
            messagebox.showwarning("Advertencia", "No estás conectado.")
            return
        filepath = filedialog.askopenfilename()
        if filepath:
            self.send_queue.put(('file', filepath))
            filename = os.path.basename(filepath)
            self.append_message(f"[Archivo enviado]: {filename}", "right")

    def update_status(self, text):
        self.status_label.config(text=text)

    def on_closing(self):
        self.running = False
        try:
            self.send_queue.put(None)  # Señal para cerrar hilo enviar
            if self.sock:
                self.sock.close()
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = ChatApp()
    app.chat_area.tag_configure("left", foreground="blue")
    app.chat_area.tag_configure("right", foreground="green")
    app.mainloop()
