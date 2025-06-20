import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os

class IDETapioka:
    def __init__(self, master):
        self.master = master
        self.file_path = None

        self.editor = scrolledtext.ScrolledText(master, font=("Courier", 12), bg="black", fg="lime", insertbackground="white")
        self.editor.pack(fill="both", expand=True)

        frame_botones = tk.Frame(master, bg="gray")
        frame_botones.pack(fill="x")

        tk.Button(frame_botones, text="Nuevo", command=self.nuevo_archivo).pack(side="left", padx=2)
        tk.Button(frame_botones, text="Abrir", command=self.abrir_archivo).pack(side="left", padx=2)
        tk.Button(frame_botones, text="Guardar", command=self.guardar_archivo).pack(side="left", padx=2)
        tk.Button(frame_botones, text="Compilar", command=self.compilar).pack(side="left", padx=2)
        tk.Button(frame_botones, text="Ejecutar", command=self.ejecutar).pack(side="left", padx=2)

        self.consola = scrolledtext.ScrolledText(master, height=10, font=("Courier", 17), bg="black", fg="white")
        self.consola.pack(fill="x")

    def nuevo_archivo(self):
        self.editor.delete(1.0, tk.END)
        self.file_path = None

    def abrir_archivo(self):
        file = filedialog.askopenfilename(filetypes=[("Archivos C", "*.c")])
        if file:
            self.file_path = file
            with open(file, "r") as f:
                contenido = f.read()
            self.editor.delete(1.0, tk.END)
            self.editor.insert(tk.END, contenido)

    def guardar_archivo(self):
        if not self.file_path:
            file = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("Archivos C", "*.c")])
            if file:
                self.file_path = file
            else:
                return
        with open(self.file_path, "w") as f:
            f.write(self.editor.get(1.0, tk.END))
        self.consola.insert(tk.END, f"Archivo guardado: {self.file_path}\n")

    def compilar(self):
        if not self.file_path:
            self.guardar_archivo()
        if self.file_path:
            output = os.path.splitext(self.file_path)[0]
            comando = ["gcc", self.file_path, "-o", output]
            try:
                resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
                self.consola.insert(tk.END, f"Compilado exitosamente: {output}\n")
            except subprocess.CalledProcessError as e:
                self.consola.insert(tk.END, f"Error de compilación:\n{e.stderr}\n")

    def ejecutar(self):
        if not self.file_path:
            self.consola.insert(tk.END, "Guarda y compila primero.\n")
            return
        output = os.path.splitext(self.file_path)[0]
        if os.path.exists(output):
            try:
                resultado = subprocess.run([output], capture_output=True, text=True, check=True)
                self.consola.insert(tk.END, f"Salida:\n{resultado.stdout}\n")
            except subprocess.CalledProcessError as e:
                self.consola.insert(tk.END, f"Error en ejecución:\n{e.stderr}\n")
        else:
            self.consola.insert(tk.END, "Compila el programa primero.\n")
