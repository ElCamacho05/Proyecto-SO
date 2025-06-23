import tkinter as tk
from tkinter import filedialog, messagebox
import os

try:
    import pygame
except ImportError:
    pygame = None

# Colores neutros suaves
BG_COLOR = "#E8E6E1"
BTN_COLOR = "#C4C3B9"
BTN_HOVER = "#A8A79D"
FONT = ("Segoe UI", 11)
LBL_COLOR = "#4A4A4A"
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "MiPC"))
os.makedirs(RAIZ, exist_ok=True)  # asegura que exista



class ReproductorWin98:
    def __init__(self, root):
        self.root = root
        if isinstance(self.root, tk.Tk):
            self.root.title("Reproductor de Audio - Win98")
            self.root.geometry("460x250")
            self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        if pygame is None:
            messagebox.showerror("Error", "pygame no está instalado.")
            self.root.destroy()
            return

        pygame.mixer.init()
        self.archivo = None
        self.reproduciendo = False
        self.pausado = False

        self.label_nombre = tk.Label(root, text="Ningún archivo cargado", bg=BG_COLOR, font=FONT, fg=LBL_COLOR)
        self.label_nombre.pack(pady=(25, 20))

        botones = tk.Frame(root, bg=BG_COLOR)
        botones.pack(pady=15)

        self.botones = []

        btn_abrir = tk.Button(botones, text="🎵 Abrir", command=self.abrir_archivo, bg=BTN_COLOR, font=FONT, width=18, relief="flat", fg=LBL_COLOR, cursor="hand2")
        btn_reproducir = tk.Button(botones, text="▶️ Reproducir", command=self.reproducir, bg=BTN_COLOR, font=FONT, width=18, relief="flat", fg=LBL_COLOR, cursor="hand2")
        btn_pausar = tk.Button(botones, text="⏸️ Pausar", command=self.pausar, bg=BTN_COLOR, font=FONT, width=18, relief="flat", fg=LBL_COLOR, cursor="hand2")
        btn_detener = tk.Button(botones, text="⏹️ Detener", command=self.detener, bg=BTN_COLOR, font=FONT, width=18, relief="flat", fg=LBL_COLOR, cursor="hand2")

        self.botones.extend([btn_abrir, btn_reproducir, btn_pausar, btn_detener])

        for i, btn in enumerate(self.botones):
            btn.grid(row=i//2, column=i%2, padx=15, pady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BTN_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BTN_COLOR))

        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            self.root.protocol("WM_DELETE_WINDOW", self.salir)
            self.root.bind("<Destroy>", self.on_destroy)

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            initialdir=RAIZ,
            title="Selecciona un archivo de audio",
            filetypes=[("Archivos de audio", "*.mp3 *.wav *.ogg")]
        )
        if ruta:
            try:
                pygame.mixer.music.load(ruta)
                self.archivo = ruta
                nombre = os.path.basename(ruta)
                if len(nombre) > 35:
                    nombre = nombre[:32] + "..."
                self.label_nombre.config(text=nombre)
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
        self.detener()  # Detiene la música
        # No hagas pygame.mixer.quit()
        self.root.destroy()

    def on_destroy(self, event):
        if event.widget == self.root:
            self.detener()
            pygame.mixer.quit()


def main():
    root = tk.Tk()
    app = ReproductorWin98(root)
    root.mainloop()

if __name__ == "__main__":
    main()
