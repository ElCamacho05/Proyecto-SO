import tkinter as tk
from tkinter import filedialog, messagebox
import os

try:
    import pygame
except ImportError:
    pygame = None

BG_COLOR = "#C0C0C0"
BTN_COLOR = "#E0E0E0"
FONT = ("MS Sans Serif", 10)

class ReproductorWin98:
    def __init__(self, root):
        self.root = root
        self.root.title("Reproductor de Audio - Win98")
        self.root.geometry("400x180")
        self.root.configure(bg=BG_COLOR)

        if pygame is None:
            messagebox.showerror("Error", "pygame no está instalado.")
            self.root.destroy()
            return

        pygame.mixer.init()
        self.archivo = None
        self.reproduciendo = False
        self.pausado = False

        self.label_nombre = tk.Label(root, text="Ningún archivo cargado", bg=BG_COLOR, font=FONT)
        self.label_nombre.pack(pady=10)

        botones = tk.Frame(root, bg=BG_COLOR)
        botones.pack(pady=5)

        tk.Button(botones, text="🎵 Abrir", command=self.abrir_archivo, bg=BTN_COLOR, font=FONT, width=8).grid(row=0, column=0, padx=5)
        tk.Button(botones, text="▶️ Reproducir", command=self.reproducir, bg=BTN_COLOR, font=FONT, width=10).grid(row=0, column=1, padx=5)
        tk.Button(botones, text="⏸️ Pausar", command=self.pausar, bg=BTN_COLOR, font=FONT, width=8).grid(row=0, column=2, padx=5)
        tk.Button(botones, text="⏹️ Detener", command=self.detener, bg=BTN_COLOR, font=FONT, width=8).grid(row=0, column=3, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.salir)

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(title="Selecciona un archivo de audio",
                                          filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")])
        if ruta:
            try:
                pygame.mixer.music.load(ruta)
                self.archivo = ruta
                self.label_nombre.config(text=os.path.basename(ruta))
                self.reproduciendo = False
                self.pausado = False
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

    def reproducir(self):
        if self.archivo:
            if not self.reproduciendo:
                pygame.mixer.music.play()
                self.reproduciendo = True
                self.pausado = False
            elif self.pausado:
                pygame.mixer.music.unpause()
                self.pausado = False
        else:
            messagebox.showwarning("Sin archivo", "Primero abre un archivo de audio.")

    def pausar(self):
        if self.reproduciendo and not self.pausado:
            pygame.mixer.music.pause()
            self.pausado = True

    def detener(self):
        if self.reproduciendo:
            pygame.mixer.music.stop()
            self.reproduciendo = False
            self.pausado = False

    def salir(self):
        self.detener()
        pygame.mixer.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ReproductorWin98(root)
    root.mainloop()

if __name__ == "__main__":
    main()
