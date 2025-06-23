import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import os

BG_COLOR = "#C0C0C0"
BTN_COLOR = "#E0E0E0"
FONT = ("MS Sans Serif", 10)
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "MiPC"))
os.makedirs(RAIZ, exist_ok=True)

class GaleriaWin98:
    def __init__(self, root):
        self.root = root
        self.root_dir = RAIZ
        self.imagenes = []

        if isinstance(self.root, (tk.Tk, tk.Toplevel)):
            self.root.title("Galería Tapioca OS")
            self.root.geometry("1000x600")
            self.root.config(bg=BG_COLOR)

            self.menu = tk.Menu(self.root, bg=BTN_COLOR, fg="black")
            archivo = tk.Menu(self.menu, tearoff=0)
            archivo.add_command(label="Cambiar carpeta raíz", command=self.seleccionar_raiz)
            archivo.add_separator()
            archivo.add_command(label="Salir", command=self.root.quit)
            self.menu.add_cascade(label="Archivo", menu=archivo)
            self.root.config(menu=self.menu)

        self.frame_principal = tk.Frame(self.root, bg=BG_COLOR)
        self.frame_principal.pack(fill="both", expand=True)

        self.panel_izquierdo = tk.Frame(self.frame_principal, bg=BG_COLOR, width=220)
        self.panel_izquierdo.pack(side="left", fill="y")

        self.panel_derecho = tk.Frame(self.frame_principal, bg=BG_COLOR)
        self.panel_derecho.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(self.panel_izquierdo)
        self.tree.pack(fill="y", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_directorio)

        self.scroll_canvas = tk.Canvas(self.panel_derecho, bg=BG_COLOR, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg=BG_COLOR)
        self.scrollbar = tk.Scrollbar(self.panel_derecho, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", self.actualizar_scroll)

        self.cargar_arbol_directorios()
        self.cargar_imagenes(self.root_dir)

    def actualizar_scroll(self, event):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.scroll_canvas.itemconfig(self.canvas_window, width=self.scroll_canvas.winfo_width())

    def seleccionar_raiz(self):
        nueva = filedialog.askdirectory(title="Selecciona la nueva carpeta raíz", initialdir=RAIZ)
        if nueva:
            self.root_dir = nueva
            self.tree.delete(*self.tree.get_children())
            self.cargar_arbol_directorios()
            self.cargar_imagenes(self.root_dir)

    def cargar_arbol_directorios(self):
        def agregar_rama(padre, ruta):
            for nombre in sorted(os.listdir(ruta)):
                fullpath = os.path.join(ruta, nombre)
                if os.path.isdir(fullpath):
                    nodo = self.tree.insert(padre, "end", text=nombre, open=False, values=[fullpath])
                    agregar_rama(nodo, fullpath)
        root_node = self.tree.insert("", "end", text=os.path.basename(self.root_dir), open=True, values=[self.root_dir])
        agregar_rama(root_node, self.root_dir)

    def seleccionar_directorio(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            ruta = self.tree.item(seleccion[0], "values")[0]
            self.cargar_imagenes(ruta)

    def cargar_imagenes(self, ruta):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.imagenes.clear()

        imagenes = []
        for dirpath, _, archivos in os.walk(ruta):
            for f in archivos:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    imagenes.append(os.path.join(dirpath, f))
            break  # evita recursividad (solo esa carpeta)

        for i, ruta_img in enumerate(imagenes):
            try:
                imagen = Image.open(ruta_img)
                imagen.thumbnail((100, 100))
                tkimg = ImageTk.PhotoImage(imagen)
                self.imagenes.append(tkimg)

                frame = tk.Frame(self.scroll_frame, bd=2, relief="groove", bg="white")
                frame.grid(row=i // 6, column=i % 6, padx=10, pady=10)

                etiqueta = tk.Label(frame, image=tkimg, bg="white")
                etiqueta.pack()
                etiqueta.bind("<Double-Button-1>", lambda e, r=ruta_img: self.ver_imagen(r))

                nombre = os.path.basename(ruta_img)
                tk.Label(frame, text=nombre, bg="white", font=("MS Sans Serif", 8), wraplength=100).pack()

                botones = tk.Frame(frame, bg="white")
                botones.pack()
                tk.Button(botones, text="📝", command=lambda r=ruta_img: self.renombrar(r), font=FONT, width=3).pack(side="left", padx=2)
                tk.Button(botones, text="🗑️", command=lambda r=ruta_img: self.borrar(r), font=FONT, width=3).pack(side="left", padx=2)

            except Exception as e:
                print(f"Error con {ruta_img}: {e}")

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
            ventana.grab_set()
            ventana.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")

    def renombrar(self, ruta):
        nuevo = simpledialog.askstring("Renombrar", "Nuevo nombre (con extensión):")
        if nuevo:
            nueva_ruta = os.path.join(os.path.dirname(ruta), nuevo)
            try:
                os.rename(ruta, nueva_ruta)
                self.cargar_imagenes(os.path.dirname(ruta))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo renombrar:\n{e}")

    def borrar(self, ruta):
        if messagebox.askyesno("Confirmar", f"¿Borrar '{os.path.basename(ruta)}'?"):
            try:
                os.remove(ruta)
                self.cargar_imagenes(os.path.dirname(ruta))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar:\n{e}")

def main():
    root = tk.Tk()
    app = GaleriaWin98(root)
    root.mainloop()

if __name__ == "__main__":
    main()
