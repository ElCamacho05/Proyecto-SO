import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import os

BG_COLOR = "#C0C0C0"
BTN_COLOR = "#E0E0E0"
FONT = ("MS Sans Serif", 10)
RAIZ = "MiPC"

class GaleriaWin98:
    def __init__(self, root):
        self.root = root
        self.root.title("Galería Tapioca OS")
        self.root.geometry("950x600")
        self.root.configure(bg=BG_COLOR)

        self.root_dir = os.path.abspath(RAIZ)
        os.makedirs(self.root_dir, exist_ok=True)
        self.imagenes = []

        self.menu = tk.Menu(self.root, bg=BTN_COLOR, fg="black")
        archivo = tk.Menu(self.menu, tearoff=0)
        archivo.add_command(label="Cambiar carpeta raíz", command=self.seleccionar_raiz)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.root.quit)
        self.menu.add_cascade(label="Archivo", menu=archivo)
        self.root.config(menu=self.menu)

        self.scroll_canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg=BG_COLOR)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", self.actualizar_scroll)

        self.cargar_imagenes()

    def actualizar_scroll(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.scroll_canvas.itemconfig(self.canvas_window, width=self.scroll_canvas.winfo_width())

    def seleccionar_raiz(self):
        nueva = filedialog.askdirectory(title="Selecciona la nueva carpeta raíz")
        if nueva:
            self.root_dir = nueva
            self.cargar_imagenes()

    def cargar_imagenes(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.imagenes.clear()

        imagenes = []
        for dirpath, _, archivos in os.walk(self.root_dir):
            for f in archivos:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    imagenes.append(os.path.join(dirpath, f))

        for i, ruta in enumerate(imagenes):
            try:
                imagen = Image.open(ruta)
                imagen.thumbnail((100, 100))
                tkimg = ImageTk.PhotoImage(imagen)
                self.imagenes.append(tkimg)

                frame = tk.Frame(self.scroll_frame, bd=2, relief="groove", bg="white")
                frame.grid(row=i // 6, column=i % 6, padx=10, pady=10)

                etiqueta = tk.Label(frame, image=tkimg, bg="white")
                etiqueta.pack()
                etiqueta.bind("<Double-Button-1>", lambda e, r=ruta: self.ver_imagen(r))

                nombre = os.path.basename(ruta)
                tk.Label(frame, text=nombre, bg="white", font=("MS Sans Serif", 8), wraplength=100).pack()

                botones = tk.Frame(frame, bg="white")
                botones.pack()
                tk.Button(botones, text="📝", command=lambda r=ruta: self.renombrar(r), font=FONT, width=3).pack(side="left", padx=2)
                tk.Button(botones, text="🗑️", command=lambda r=ruta: self.borrar(r), font=FONT, width=3).pack(side="left", padx=2)

            except Exception as e:
                print(f"Error con {ruta}: {e}")

    def ver_imagen(self, ruta):
        try:
            ventana = tk.Toplevel(self.root)
            ventana.title(os.path.basename(ruta))
            imagen = Image.open(ruta)
            imagen.thumbnail((700, 500))
            tkimg = ImageTk.PhotoImage(imagen)
            label = tk.Label(ventana, image=tkimg)
            label.image = tkimg
            label.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")

    def renombrar(self, ruta):
        nuevo = simpledialog.askstring("Renombrar", "Nuevo nombre (con extensión):")
        if nuevo:
            nueva_ruta = os.path.join(os.path.dirname(ruta), nuevo)
            try:
                os.rename(ruta, nueva_ruta)
                self.cargar_imagenes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo renombrar:\n{e}")

    def borrar(self, ruta):
        if messagebox.askyesno("Confirmar", f"¿Borrar '{os.path.basename(ruta)}'?"):
            try:
                os.remove(ruta)
                self.cargar_imagenes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar:\n{e}")

def main():
    root = tk.Tk()
    app = GaleriaWin98(root)
    root.mainloop()

if __name__ == "__main__":
    main()
