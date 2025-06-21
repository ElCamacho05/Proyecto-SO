import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class BlocNotas98:
    def __init__(self, master, ruta=None):
        self.master = master  # Este es un frame o ventana embebida
        directorio_actual_archivo = os.path.dirname(os.path.abspath(__file__))
        self.base = os.path.abspath(os.path.join(directorio_actual_archivo, "..", "apps", "MiPC"))
        self.ruta = ruta

        self.master.configure(bg="#C0C0C0")

        self.texto = tk.Text(self.master, wrap="word", font=("Courier New", 10), bg="white", fg="black")
        self.texto.pack(fill="both", expand=True)

        self.crear_menu()

        if self.ruta:
            self.abrir_archivo(self.ruta)

    def crear_menu(self):
        menu = tk.Menu(self.master, bg="#E0E0E0", fg="black", activebackground="#000080", activeforeground="white")

        archivo = tk.Menu(menu, tearoff=0)
        archivo.add_command(label="Nuevo", command=self.nuevo_archivo)
        archivo.add_command(label="Abrir...", command=self.abrir_dialogo)
        archivo.add_command(label="Guardar", command=self.guardar_archivo)
        archivo.add_command(label="Guardar como...", command=self.guardar_como)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=lambda: self.master.destroy())

        menu.add_cascade(label="Archivo", menu=archivo)
        try:
            self.master.config(menu=menu)
        except:
            pass  # Puede no funcionar si se embebe en un Frame, lo manejamos desde interfaz

    def nuevo_archivo(self):
        self.ruta = None
        self.texto.delete("1.0", tk.END)

    def abrir_dialogo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if ruta:
            self.abrir_archivo(ruta)

    def abrir_archivo(self, ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.texto.delete("1.0", tk.END)
            self.texto.insert("1.0", contenido)
            self.ruta = ruta
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    def guardar_archivo(self):
        if not self.ruta:
            return self.guardar_como()
        try:
            with open(self.ruta, "w", encoding="utf-8") as f:
                f.write(self.texto.get("1.0", "end-1c"))
            messagebox.showinfo("Guardado", "Archivo guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")], initialdir=self.base)
        if ruta:
            self.ruta = ruta
            self.guardar_archivo()

def main():
    ruta_archivo = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    app = BlocNotas98(root, ruta_archivo)
    root.mainloop()

if __name__ == "__main__":
    main()
