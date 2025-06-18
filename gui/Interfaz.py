# interfaz.py

import tkinter as tk
from tkinter import scrolledtext
import time
from apps.TerminalSO import TerminalSO

ventanas_abiertas = []

def crear_terminal_contenida(contenedor, barra_tareas):
    frame_terminal = tk.Frame(contenedor, bg="gray", bd=2, relief="raised")
    frame_terminal.place(x=200, y=100, width=700, height=500)
    ventanas_abiertas.append(frame_terminal)

    barra = tk.Frame(frame_terminal, bg="navy", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="Terminal - Tapioca OS", bg="navy", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    def iniciar_movimiento(event):
        frame_terminal.startX = event.x
        frame_terminal.startY = event.y

    def mover_ventana(event):
        x = frame_terminal.winfo_x() + (event.x - frame_terminal.startX)
        y = frame_terminal.winfo_y() + (event.y - frame_terminal.startY)
        frame_terminal.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    salida = scrolledtext.ScrolledText(frame_terminal, bg="black", fg="lime", insertbackground="white", font=("Courier", 10))
    salida.pack(fill="both", expand=True)
    salida.config(state="disabled")

    entrada = tk.Entry(frame_terminal, font=("Courier", 10), bg="gray10", fg="white", insertbackground="white")
    entrada.pack(fill="x")

    boton_tarea = tk.Button(barra_tareas, text="Terminal", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_terminal.lift())
    boton_tarea.pack(side="left", padx=2)

    terminal = TerminalSO(salida, frame_terminal, boton_tarea, entrada)

    def ejecutar_desde_gui(event):
        comando = entrada.get()
        terminal.escribir(f"$ {comando}")
        entrada.delete(0, tk.END)
        terminal.ejecutar_comando(comando)

    entrada.bind("<Return>", ejecutar_desde_gui)
    terminal.mostrar_ayuda()

def toggle_menu():
    if menu_inicio.winfo_ismapped():
        menu_inicio.place_forget()
    else:
        menu_inicio.place(x=10, y=root.winfo_height() - 160)

def actualizar_reloj():
    reloj.config(text=time.strftime('%H:%M'))
    root.after(60000, actualizar_reloj)

# === Ventana principal ===
root = tk.Tk()
root.title("Tapioca OS - Escritorio Estilo Win98")
root.geometry("1024x700")
root.config(bg="#008080")

barra_tareas = tk.Frame(root, bg="#C0C0C0", height=40, bd=2, relief="raised")
barra_tareas.pack(side="bottom", fill="x")

boton_inicio = tk.Button(barra_tareas, text="Inicio", font=("MS Sans Serif", 10, "bold"),
                         bg="#C0C0C0", fg="black", relief="raised", command=toggle_menu)
boton_inicio.pack(side="left", padx=5)

reloj = tk.Label(barra_tareas, text="", font=("MS Sans Serif", 9), bg="#C0C0C0", fg="black", anchor="e")
reloj.pack(side="right", padx=10)
actualizar_reloj()

menu_inicio = tk.Frame(root, bg="#C0C0C0", bd=2, relief="raised")

tk.Button(menu_inicio, text="Terminal", width=20, anchor="w",
          command=lambda:[crear_terminal_contenida(root, barra_tareas), toggle_menu()]).pack(pady=1)
tk.Button(menu_inicio, text="Calculadora (próximamente)", width=20, anchor="w", state="disabled").pack(pady=1)
tk.Button(menu_inicio, text="Bloc de notas (próximamente)", width=20, anchor="w", state="disabled").pack(pady=1)

root.mainloop()
