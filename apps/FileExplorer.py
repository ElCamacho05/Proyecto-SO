import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import mimetypes
import subprocess
import time
import platform

BG_COLOR = "#C0C0C0"
BTN_COLOR = "#E0E0E0"
FONT = ("MS Sans Serif", 10)
ROOT_DIR = os.path.abspath("MiPC")

class ExploradorWin98:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorador de Archivos - Windows 98")
        self.root.geometry("800x550")
        self.root.configure(bg=BG_COLOR)
        os.makedirs(ROOT_DIR, exist_ok=True)
        self.crear_widgets()
        self.cargar_arbol()

    def crear_widgets(self):
        barra = tk.Frame(self.root, bg=BG_COLOR, bd=2, relief="raised")
        barra.pack(side="top", fill="x")

        acciones = [
            ("Crear Carpeta", self.crear_carpeta),
            ("Crear Archivo", self.crear_archivo),
            ("Eliminar", self.eliminar_elemento),
            ("Renombrar", self.renombrar_elemento),
            ("Abrir", self.abrir_archivo),
            ("Propiedades", self.ver_propiedades)
        ]
        for texto, comando in acciones:
            tk.Button(barra, text=texto, bg=BTN_COLOR, font=FONT, command=comando).pack(side="left", padx=3)

        self.arbol = ttk.Treeview(self.root)
        self.arbol.pack(fill="both", expand=True, padx=5, pady=5)
        self.arbol.bind("<Double-1>", self.navegar)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", font=FONT, background=BG_COLOR, fieldbackground=BG_COLOR)
        estilo.map("Treeview", background=[("selected", "#000080")], foreground=[("selected", "#FFFFFF")])

        self.scroll = ttk.Scrollbar(self.arbol, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscroll=self.scroll.set)
        self.scroll.pack(side="right", fill="y")

    def cargar_arbol(self):
        self.arbol.delete(*self.arbol.get_children())
        self.insertar_elementos("", ROOT_DIR)

    def insertar_elementos(self, padre, ruta):
        try:
            for nombre in sorted(os.listdir(ruta)):
                ruta_completa = os.path.join(ruta, nombre)
                nodo = self.arbol.insert(padre, "end", text=nombre, values=[ruta_completa], open=False)
                if os.path.isdir(ruta_completa):
                    self.insertar_elementos(nodo, ruta_completa)
        except PermissionError:
            pass

    def navegar(self, evento):
        item = self.arbol.focus()
        ruta = self.arbol.item(item, "values")[0]
        if os.path.isdir(ruta):
            self.arbol.item(item, open=not self.arbol.item(item, "open"))

    def crear_carpeta(self):
        ruta_padre = self.obtener_ruta_actual()
        nombre = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
        if nombre:
            nueva_ruta = os.path.join(ruta_padre, nombre)
            try:
                os.makedirs(nueva_ruta)
                self.cargar_arbol()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def crear_archivo(self):
        ruta_padre = self.obtener_ruta_actual()
        nombre = simpledialog.askstring("Nuevo Archivo", "Nombre del archivo:")
        if nombre:
            nueva_ruta = os.path.join(ruta_padre, nombre)
            try:
                with open(nueva_ruta, "w") as f:
                    f.write("")
                self.cargar_arbol()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def eliminar_elemento(self):
        ruta = self.obtener_ruta_seleccionada()
        if ruta and messagebox.askyesno("Confirmar", f"¿Eliminar '{os.path.basename(ruta)}'?"):
            try:
                if os.path.isdir(ruta):
                    os.rmdir(ruta)
                else:
                    os.remove(ruta)
                self.cargar_arbol()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def renombrar_elemento(self):
        ruta = self.obtener_ruta_seleccionada()
        if ruta:
            nuevo_nombre = simpledialog.askstring("Renombrar", "Nuevo nombre:")
            if nuevo_nombre:
                nuevo_path = os.path.join(os.path.dirname(ruta), nuevo_nombre)
                try:
                    os.rename(ruta, nuevo_path)
                    self.cargar_arbol()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def abrir_archivo(self):
        ruta = self.obtener_ruta_seleccionada()
        if ruta and os.path.isfile(ruta):
            try:
                if platform.system() == "Windows":
                    os.startfile(ruta)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", ruta])
                else:
                    subprocess.Popen(["xdg-open", ruta])
            except Exception as e:
                messagebox.showerror("Error al abrir archivo", str(e))

    def ver_propiedades(self):
        ruta = self.obtener_ruta_seleccionada()
        if ruta:
            try:
                nombre = os.path.basename(ruta)
                tipo = "Carpeta" if os.path.isdir(ruta) else "Archivo"
                tam = os.path.getsize(ruta)
                modificado = time.ctime(os.path.getmtime(ruta))
                info = f"Nombre: {nombre}\nTipo: {tipo}\nTamaño: {tam} bytes\nÚltima modificación: {modificado}"
                messagebox.showinfo("Propiedades", info)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def obtener_ruta_actual(self):
        item = self.arbol.focus()
        return self.arbol.item(item, "values")[0] if item else ROOT_DIR

    def obtener_ruta_seleccionada(self):
        item = self.arbol.focus()
        return self.arbol.item(item, "values")[0] if item else None

if __name__ == "__main__":
    root = tk.Tk()
    app = ExploradorWin98(root)
    root.mainloop()
