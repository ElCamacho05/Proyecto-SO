# interfaz.py

import tkinter as tk
from tkinter import scrolledtext
import time
from apps.TerminalSO import TerminalSO
from apps.Calculadora import Calculadora
from kernel.usario import registrar_usuario, iniciar_sesion
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import hashlib
import itertools
import threading

# ================== CONFIGURACIÓN GENERAL =====================

PALETA = {
    'fondo': '#f2c6b4',       # Rosa pastel
    'fondos_animados': ['#f2c6b4', '#f4a261', '#ffe8cc', '#e9c46a', '#f7c59f'],
    'barra': '#f4a261',       # Naranja suave
    'ventana': '#ffe8cc',     # Beige claro
    'texto': '#222222',       # Casi negro
    'boton': '#e76f51',       # Rojo coral
    'boton_fg': '#fff8f0',    # Blanco hueso
    'borde': '#7f5539',       # Marrón oscuro
}

FUENTE_TITULO = ("Courier New", 24, "bold")
FUENTE_NORMAL = ("Courier New", 14)

# ================== VENTANA PRINCIPAL =====================
ventanas_abiertas = []
ventana = tk.Tk()
ventana.title("Tapioka OS")
ventana.geometry("1024x700")
ventana.config(bg=PALETA['fondo'])

# ================== FONDO =====================
fondo_img = Image.open("../Assets/background.jpg")
#fondo_img_tk = ImageTk.PhotoImage(fondo_img)

# ================== LOGO TAPIOKA =====================
logo_img = Image.open("../Assets/LOGO.png")  # Ajusta la ruta y nombre de archivo

canvas = tk.Canvas(ventana,highlightthickness=0)
canvas.pack(fill="both", expand=True)
#canvas.create_image(0, 0, anchor="nw", image=fondo_img_tk)

fondo_tk = ImageTk.PhotoImage(fondo_img)
logo_tk = ImageTk.PhotoImage(logo_img)

canvas.create_image(0, 0, anchor="nw", image=fondo_tk)
logo_x = 960  # centro horizontal
logo_y = 0   # 50 píxeles desde arriba
canvas.create_image(logo_x, logo_y, anchor="n", image=logo_tk)

# ================== FRAME PRINCIPAL =====================
main_frame = tk.Frame(canvas, bg=PALETA['fondo'])
main_frame.place(relx=0.5, rely=0.6, anchor="center")

# ========== Funciones auxiliares ==========
def hash_contraseña(contra):
    return hashlib.sha256(contra.encode()).hexdigest()

def registrar_usuario(nombre, usuario, contra, rol, correo, fecha, mascota, escuela, ciudad, amor):
    with open("USUARIOS.TXT", "r", encoding="utf-8") as f:
        if usuario in f.read():
            return False

    with open("USUARIOS.TXT", "a", encoding="utf-8") as f:
        f.write(f"""Nombre: {nombre}
Nombre de usuario: {usuario}
Contrasena: {hash_contraseña(contra)}
Rol: {rol}
Correo: {correo}
Fecha de nacimiento: {fecha}
Mascota: {mascota}
Escuela: {escuela}
Ciudad natal: {ciudad}
Primer amor: {amor}
----------------------------------------
""")
    return True

def iniciar_sesion(usuario, contra):
    hash_ingresado = hash_contraseña(contra)
    with open("USUARIOS.TXT", "r", encoding="utf-8") as f:
        contenido = f.read()
        bloques = contenido.split("----------------------------------------")
        for bloque in bloques:
            if f"Nombre de usuario: {usuario}" in bloque and f"Contrasena: {hash_ingresado}" in bloque:
                for linea in bloque.splitlines():
                    if linea.startswith("Rol:"):
                        return linea.replace("Rol:", "").strip()
    return None


# ================== FUNCIONES =====================
def limpiar_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

def mostrar_login():
    limpiar_frame()
    #login_win = tk.Tk()
    #login_win.title("Login - Tapioka OS")
    #login_win.geometry("700x500")
    tk.Label(main_frame, text="Bienvenido a Tapioka OS", bg=PALETA['fondo'], fg=PALETA['texto'], font=FUENTE_TITULO).pack(pady=15)

    tk.Label(main_frame, text="Usuario:", bg=PALETA['fondo'], fg=PALETA['texto'], font=FUENTE_NORMAL).pack()
    entry_usuario = tk.Entry(main_frame, font=FUENTE_NORMAL, width=30)
    entry_usuario.pack(pady=5)

    tk.Label(main_frame, text="Contraseña:", bg=PALETA['fondo'], fg=PALETA['texto'], font=FUENTE_NORMAL).pack()
    entry_contra = tk.Entry(main_frame, show="*", font=FUENTE_NORMAL, width=30)
    entry_contra.pack(pady=5)

    def login():
        usuario = entry_usuario.get()
        contraseña = entry_contra.get()
        rol = iniciar_sesion(usuario, contraseña)

        if rol:
            messagebox.showinfo("Bienvenido", f"Acceso como {rol}")
            mostrar_escritorio()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    tk.Button(main_frame, text="Iniciar sesión", font=FUENTE_NORMAL, bg=PALETA['boton'], fg=PALETA['boton_fg'],
              command=login).pack(pady=15)

    tk.Button(main_frame, text="Registrarse", font=FUENTE_NORMAL, bg=PALETA['barra'], fg=PALETA['texto'],
              command=mostrar_registro).pack(pady=5)

    #fondo.image = fondo_img_tk

def mostrar_registro():
    limpiar_frame()
    tk.Label(main_frame, text="Registro de Usuario", bg=PALETA['fondo'], fg=PALETA['texto'], font=FUENTE_NORMAL).pack(pady=10)

    campos = {}
    etiquetas = [
        ("Nombre completo", "nombre"),
        ("Nombre de usuario", "usuario"),
        ("Contraseña", "contraseña"),
        ("Rol (admin/invitado)", "rol"),
        ("Correo electrónico", "correo"),
        ("Fecha de nacimiento (DD/MM/AAAA)", "fecha"),
        ("Tu primera mascota", "mascota"),
        ("Tu escuela primaria", "escuela"),
        ("Ciudad natal", "ciudad"),
        ("Primer amor", "amor"),
    ]

    for texto, clave in etiquetas:
        tk.Label(main_frame, text=texto, font=FUENTE_NORMAL, bg=PALETA['fondo'], fg=PALETA['texto']).pack(pady=(5, 0))
        show = "*" if clave == "contraseña" else None
        entry = tk.Entry(main_frame, font=FUENTE_NORMAL, bg="white", fg=PALETA['texto'], show=show)
        entry.pack(pady=3)
        campos[clave] = entry


    def registrar():
        datos = {k: v.get().strip() for k, v in campos.items()}
        if "" in datos.values():
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        exito = registrar_usuario(
            datos["nombre"], datos["usuario"], datos["contraseña"],
            datos["rol"], datos["correo"], datos["fecha"],
            datos["mascota"], datos["escuela"], datos["ciudad"], datos["amor"]
        )
        if exito:
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            mostrar_login()
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

    tk.Button(main_frame, text="Registrar", font=FUENTE_NORMAL, bg=PALETA['boton'], fg=PALETA['boton_fg'],
            command=registrar).pack(pady=15)

    tk.Button(main_frame, text="Volver", font=FUENTE_NORMAL, bg=PALETA['barra'], fg=PALETA['texto'],
            command=mostrar_login).pack()

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

    terminal = TerminalSO(salida, frame_terminal, boton_tarea, entrada, ventanas_abiertas)

    def ejecutar_desde_gui(event):
        comando = entrada.get()
        terminal.escribir(f"$ {comando}")
        entrada.delete(0, tk.END)
        terminal.ejecutar_comando(comando)

    entrada.bind("<Return>", ejecutar_desde_gui)
    terminal.mostrar_ayuda()

def crear_calculadora_contenida(contenedor, barra_tareas):
    frame_calc = tk.Frame(contenedor, bg="gray", bd=2, relief="raised")
    frame_calc.place(x=250, y=150, width=300, height=350)
    ventanas_abiertas.append(frame_calc)

    barra = tk.Frame(frame_calc, bg="darkred", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="Calculadora - Tapioca OS", bg="darkred", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkred", fg="white", bd=0,
                             command=lambda: cerrar_calculadora(frame_calc, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        frame_calc.startX = event.x_root - frame_calc.winfo_rootx()
        frame_calc.startY = event.y_root - frame_calc.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - frame_calc.startX
        y = event.y_root - frame_calc.startY
        frame_calc.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="Calculadora", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_calc.lift())
    boton_tarea.pack(side="left", padx=2)

    Calculadora(frame_calc, boton_tarea)

def cerrar_calculadora(ventana, boton):
    ventana.destroy()
    boton.destroy()

def toggle_menu():
    if menu_inicio.winfo_ismapped():
        menu_inicio.place_forget()
    else:
        menu_inicio.place(x=10, y=escritorio.winfo_height() - 160)

def actualizar_reloj():
    reloj.config(text=time.strftime('%H:%M'))
    escritorio.after(60000, actualizar_reloj)

def mostrar_escritorio():
    limpiar_frame()

    global escritorio, reloj, menu_inicio

    escritorio = tk.Frame(canvas, bg=PALETA['ventana'], bd=4, relief="ridge")
    escritorio.pack(expand=True, fill="both")

    barra_tareas = tk.Frame(escritorio, bg=PALETA['fondo'], height=40, bd=2, relief="raised")
    barra_tareas.pack(side="bottom", fill="x")

    boton_inicio = tk.Button(barra_tareas, text="Inicio", font=("MS Sans Serif", 10, "bold"),
                             bg=PALETA['fondo'], fg="black", relief="raised", command=toggle_menu)
    boton_inicio.pack(side="left", padx=5)

    reloj = tk.Label(barra_tareas, text="", font=("MS Sans Serif", 9), bg=PALETA['fondo'], fg="black", anchor="e")
    reloj.pack(side="right", padx=10)
    actualizar_reloj()

    menu_inicio = tk.Frame(escritorio, bg="#C0C0C0", bd=2, relief="raised")

    tk.Button(menu_inicio, text="Terminal", width=20, anchor="w",
              command=lambda:[crear_terminal_contenida(escritorio, barra_tareas), toggle_menu()]).pack(pady=1)
    tk.Button(menu_inicio, text="Calculadora", width=20, anchor="w",
              command=lambda:[crear_calculadora_contenida(escritorio, barra_tareas), toggle_menu()]).pack(pady=1)
    tk.Button(menu_inicio, text="Bloc de notas (próximamente)", width=20, anchor="w", state="disabled").pack(pady=1)

    #root.mainloop()

if __name__ == "__main__":
    mostrar_login()
    #mostrar_escritorio()
    ventana.mainloop()