# apps/Calculadora.py
import tkinter as tk

class Calculadora:
    def __init__(self, frame_padre, boton_tarea):
        self.frame = frame_padre
        self.boton_tarea = boton_tarea

        self.pantalla = tk.Entry(self.frame, font=("Courier", 16), justify="right")
        self.pantalla.pack(fill="x", padx=10, pady=10)

        botones = [
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("0", ".", "=", "+")
        ]

        for fila in botones:
            fila_frame = tk.Frame(self.frame)
            fila_frame.pack(expand=True, fill="both")
            for btn in fila:
                b = tk.Button(fila_frame, text=btn, font=("Courier", 14), width=5, height=2,
                              command=lambda x=btn: self.procesar(x))
                b.pack(side="left", expand=True, fill="both")

    def procesar(self, valor):
        if valor == "=":
            try:
                resultado = eval(self.pantalla.get())
                self.pantalla.delete(0, tk.END)
                self.pantalla.insert(tk.END, str(resultado))
            except Exception:
                self.pantalla.delete(0, tk.END)
                self.pantalla.insert(tk.END, "Error")
        else:
            self.pantalla.insert(tk.END, valor)