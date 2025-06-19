import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk

import time
from apps.TerminalSO import TerminalSO
from apps.Calculadora import Calculadora
from kernel.usario import registrar_usuario, iniciar_sesion

fondo_img_global = None

ventanas_abiertas = []

# === Ventana principal ===
root = tk.Tk()
root.title("Tapioca OS - Escritorio Estilo Win98")
root.geometry("1024x700")
root.config(bg="#008080")

# === Marco principal para contenido dinámico ===
main_frame = tk.Frame(root, bg="#008080")
main_frame.pack(fill="both", expand=True)

# === Barra de tareas ===
barra_tareas = tk.Frame(root, bg="#C0C0C0", height=40, bd=2, relief="raised")
barra_tareas.pack(side="bottom", fill="x")

# === Reloj ===
reloj = tk.Label(barra_tareas, text="", font=("MS Sans Serif", 9), bg="#C0C0C0", fg="black", anchor="e")
reloj.pack(side="right", padx=10)

def actualizar_reloj():
    reloj.config(text=time.strftime('%H:%M'))
    root.after(60000, actualizar_reloj)

actualizar_reloj()

# === Menú inicio ===
menu_inicio = tk.Frame(root, bg="#C0C0C0", bd=2, relief="raised")

def toggle_menu():
    if menu_inicio.winfo_ismapped():
        menu_inicio.place_forget()
    else:
        menu_inicio.place(x=10, y=root.winfo_height() - 160)

boton_inicio = tk.Button(barra_tareas, text="Inicio", font=("MS Sans Serif", 10, "bold"),
                         bg="#C0C0C0", fg="black", relief="raised", command=toggle_menu)
boton_inicio.pack(side="left", padx=5)

def limpiar_main_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

def asignar_items():
    global main_frame, barra_tareas, reloj, menu_inicio, boton_inicio

    main_frame = tk.Frame(root, bg="#008080")
    main_frame.pack(fill="both", expand=True)

    barra_tareas = tk.Frame(root, bg="#C0C0C0", height=40, bd=2, relief="raised")
    barra_tareas.pack(side="bottom", fill="x")

    reloj = tk.Label(barra_tareas, text="", font=("MS Sans Serif", 9), bg="#C0C0C0", fg="black", anchor="e")
    reloj.pack(side="right", padx=10)

    actualizar_reloj()

    menu_inicio = tk.Frame(root, bg="#C0C0C0", bd=2, relief="raised")

    boton_inicio = tk.Button(barra_tareas, text="Inicio", font=("MS Sans Serif", 10, "bold"),
                             bg="#C0C0C0", fg="black", relief="raised", command=toggle_menu)
    boton_inicio.pack(side="left", padx=5)


def asignar_items_legacy1():
    global root, main_frame, barra_tareas, reloj, menu_inicio, boton_inicio

    root = tk.Tk()
    root.title("Tapioca OS - Escritorio Estilo Win98")
    root.geometry("1024x700")
    root.config(bg="#008080")

    main_frame = tk.Frame(root, bg="#008080")
    main_frame.pack(fill="both", expand=True)

    barra_tareas = tk.Frame(root, bg="#C0C0C0", height=40, bd=2, relief="raised")
    barra_tareas.pack(side="bottom", fill="x")

    reloj = tk.Label(barra_tareas, text="", font=("MS Sans Serif", 9), bg="#C0C0C0", fg="black", anchor="e")
    reloj.pack(side="right", padx=10)

    actualizar_reloj()

    menu_inicio = tk.Frame(root, bg="#C0C0C0", bd=2, relief="raised")

    boton_inicio = tk.Button(barra_tareas, text="Inicio", font=("MS Sans Serif", 10, "bold"),
                             bg="#C0C0C0", fg="black", relief="raised", command=toggle_menu)
    boton_inicio.pack(side="left", padx=5)

def mostrar_login():
    limpiar_main_frame()

    # Canvas
    fondo = tk.Canvas(main_frame, width=1024, height=700, highlightthickness=0)
    fondo.pack(fill="both", expand=True)

    # Cargar y mantener la imagen como atributo del canvas (clave)
    imagen_original = Image.open("../Assets/Background.png")
    imagen_original = imagen_original.resize((1024, 700), Image.Resampling.LANCZOS)
    # fondo.fondo_img = ImageTk.PhotoImage(imagen_original)  # ← aquí se evita el garbage collection
    fondo_img = ImageTk.PhotoImage(imagen_original, master=root)
    fondo.fondo_img = fondo_img  # Fuerza la retención


    fondo.create_image(0, 0, image=fondo.fondo_img, anchor="nw")  # ← usa el atributo del canvas

    # Login UI
    marco = tk.Frame(fondo, bg="#C0C0C0", bd=3, relief="ridge")
    marco.place(relx=0.5, rely=0.5, anchor="center", width=360, height=260)

    fuente_label = ("MS Sans Serif", 14, "bold")
    fuente_entry = ("MS Sans Serif", 12)
    color_texto = "#000000"

    tk.Label(marco, text="Nombre de usuario", bg="#C0C0C0", font=fuente_label).pack(pady=(20, 2))
    entry_usuario = tk.Entry(marco, font=fuente_entry, width=30, fg=color_texto, bg="white", insertbackground=color_texto)
    entry_usuario.pack(pady=(0, 10))

    tk.Label(marco, text="Contraseña", bg="#C0C0C0", font=fuente_label).pack(pady=(15, 5))
    entry_contrasena = tk.Entry(marco, font=fuente_entry, show="*", width=25)
    entry_contrasena.pack(pady=5)

    def login():
        usuario = entry_usuario.get()
        contrasena = entry_contrasena.get()
        rol = iniciar_sesion(usuario, contrasena)

        if rol:
            messagebox.showinfo("Bienvenido", f"Acceso como {rol}")
            mostrar_escritorio()
        else:
            messagebox.showerror("ERROR", "Usuario o contraseña incorrectos")

    def ir_a_registro():
        mostrar_registro()

    tk.Button(marco, text="Iniciar sesión", bg="#4CAF50", fg="white", font=fuente_label,
              width=30, command=login).pack(pady=(10, 20))

    tk.Button(fondo, text="Registrarse", bg="#2196F3", fg="white", font=fuente_label,
              command=ir_a_registro).place(x=190, y=570)

def mostrar_login_legacy1():
    limpiar_main_frame()

    # Canvas en main_frame
    fondo = tk.Canvas(main_frame, width=1024, height=700, highlightthickness=0)
    fondo.pack(fill="both", expand=True)

    # Cargar imagen con PIL y convertirla correctamente
    imagen_original = Image.open("../Assets/Background.png")
    imagen_original = imagen_original.resize((1024, 700), Image.Resampling.LANCZOS)
    fondo_img = ImageTk.PhotoImage(imagen_original)

    # IMPORTANTE: guardar referencia a la imagen
    fondo.image = fondo_img

    # Mostrar imagen
    fondo.create_image(0, 0, image=fondo_img, anchor="nw")

    # Formulario login
    marco = tk.Frame(fondo, bg="#C0C0C0", bd=3, relief="ridge")
    marco.place(relx=0.5, rely=0.5, anchor="center", width=360, height=260)

    fuente_label = ("MS Sans Serif", 14, "bold")
    fuente_entry = ("MS Sans Serif", 12)
    color_texto = "#000000"

    tk.Label(marco, text="Nombre de usuario", bg="#C0C0C0", font=fuente_label).pack(pady=(20, 2))
    entry_usuario = tk.Entry(marco, font=fuente_entry, width=30, fg=color_texto, bg="white",
                             insertbackground=color_texto)
    entry_usuario.pack(pady=(0, 10))

    tk.Label(marco, text="Contraseña", bg="#C0C0C0", font=fuente_label).pack(pady=(15, 5))
    entry_contraseña = tk.Entry(marco, font=fuente_entry, show="*", width=25)
    entry_contraseña.pack(pady=5)

    def login():
        usuario = entry_usuario.get()
        contraseña = entry_contraseña.get()
        rol = iniciar_sesion(usuario, contraseña)

        if rol:
            messagebox.showinfo("Bienvenido", f"Acceso como {rol}")
            mostrar_escritorio()
        else:
            messagebox.showerror("ERROR", "Usuario o contraseña incorrectos")

    def ir_a_registro():
        mostrar_registro()

    tk.Button(marco, text="Iniciar sesión", bg="#4CAF50", fg="white", font=fuente_label,
              width=30, command=login).pack(pady=(10, 20))

    tk.Button(fondo, text="Registrarse", bg="#2196F3", fg="white", font=fuente_label,
              command=ir_a_registro).place(x=190, y=570)

def mostrar_login_legacy2():
    limpiar_main_frame()

    fondo = tk.Canvas(main_frame, width=1024, height=700, highlightthickness=0)
    fondo.pack(fill="both", expand=True)

    # Cargar y redimensionar imagen con PIL
    imagen_original = Image.open("../Assets/Background.png")
    imagen_original.thumbnail((1024, 700), Image.Resampling.LANCZOS)

    w_img, h_img = imagen_original.size
    x_offset = (1024 - w_img) // 2
    y_offset = (700 - h_img) // 2

    fondo_img = ImageTk.PhotoImage(imagen_original)

    # MANTENER referencia viva → evitar que se borre
    fondo.image = fondo_img

    # Mostrar imagen como fondo
    fondo.create_image(x_offset, y_offset, image=fondo_img, anchor="nw")

    # Marco de login
    marco = tk.Frame(fondo, bg="#C0C0C0", bd=3, relief="ridge")
    marco.place(relx=0.5, rely=0.5, anchor="center", width=360, height=260)

    fuente_label = ("MS Sans Serif", 14, "bold")
    fuente_entry = ("MS Sans Serif", 12)
    color_texto = "#000000"

    tk.Label(marco, text="Nombre de usuario", bg="#C0C0C0", font=fuente_label).pack(pady=(20, 2))
    entry_usuario = tk.Entry(marco, font=fuente_entry, width=30, fg=color_texto, bg="white", insertbackground=color_texto)
    entry_usuario.pack(pady=(0, 10))

    tk.Label(marco, text="Contraseña", bg="#C0C0C0", font=fuente_label).pack(pady=(15, 5))
    entry_contrasena = tk.Entry(marco, font=fuente_entry, show="*", width=25)
    entry_contrasena.pack(pady=5)

    def login():
        usuario = entry_usuario.get()
        contrasena = entry_contrasena.get()
        rol = iniciar_sesion(usuario, contrasena)

        if rol:
            messagebox.showinfo("Bienvenido", f"Acceso como {rol}")
            mostrar_escritorio()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def ir_a_registro():
        mostrar_registro()

    tk.Button(marco, text="Iniciar sesión", bg="#4CAF50", fg="white", font=fuente_label,
              width=30, command=login).pack(pady=(10, 20))

    tk.Button(fondo, text="Registrarse", bg="#2196F3", fg="white", font=fuente_label,
              command=ir_a_registro).place(x=190, y=570)

def mostrar_login_legacy3():
    limpiar_main_frame()

    fondo = tk.Canvas(main_frame, width=1024, height=700, highlightthickness=0)
    fondo.pack(fill="both", expand=True)

    # Cargar y redimensionar imagen con PIL
    imagen_original = Image.open("../Assets/Background.png")
    imagen_original.thumbnail((1024, 700), Image.Resampling.LANCZOS)

    w_img, h_img = imagen_original.size
    x_offset = (1024 - w_img) // 2
    y_offset = (700 - h_img) // 2

    fondo_img = ImageTk.PhotoImage(imagen_original)

    # 💡 Aquí está la diferencia clave
    fondo.fondo_img = fondo_img  # Guarda referencia para que no se pierda

    # Usa la imagen correctamente
    label_fondo = tk.Label(fondo, image=fondo_img)
    label_fondo.image = fondo_img  # También aquí, por seguridad
    label_fondo.place(x=x_offset, y=y_offset)

    marco = tk.Frame(fondo, bg="#C0C0C0", bd=3, relief="ridge")
    marco.place(relx=0.5, rely=0.5, anchor="center", width=360, height=260)

    fuente_label = ("MS Sans Serif", 14, "bold")
    fuente_entry = ("MS Sans Serif", 12)
    color_texto = "#000000"

    tk.Label(marco, text="Nombre de usuario", bg="#C0C0C0", font=fuente_label).pack(pady=(20, 2))
    entry_usuario = tk.Entry(marco, font=fuente_entry, width=30, fg=color_texto, bg="white", insertbackground=color_texto)
    entry_usuario.pack(pady=(0, 10))

    tk.Label(marco, text="Contraseña", bg="#C0C0C0", font=fuente_label).pack(pady=(15, 5))
    entry_contrasena = tk.Entry(marco, font=fuente_entry, show="*", width=25)
    entry_contrasena.pack(pady=5)

    def login():
        usuario = entry_usuario.get()
        contrasena = entry_contrasena.get()
        rol = iniciar_sesion(usuario, contrasena)

        if rol:
            messagebox.showinfo("Bienvenido", f"Acceso como {rol}")
            mostrar_escritorio()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def ir_a_registro():
        mostrar_registro()

    tk.Button(marco, text="Iniciar sesión", bg="#4CAF50", fg="white", font=fuente_label,
              width=30, command=login).pack(pady=(10, 20))

    tk.Button(fondo, text="Registrarse", bg="#2196F3", fg="white", font=fuente_label,
              command=ir_a_registro).place(x=190, y=570)

def mostrar_registro():
    limpiar_main_frame()
    reg_frame = tk.Frame(main_frame, bg="#fff3e0")
    reg_frame.pack(expand=True)

    campos = {}
    etiquetas = [
        ("Nombre completo", "nombre"),
        ("Nombre de usuario", "usuario"),
        ("Contraseña", "contrasena"),
        ("Rol (admin/invitado)", "rol"),
        ("Correo electrónico", "correo"),
        ("Fecha de nacimiento (DD/MM/AAAA)", "fecha"),
        ("Tu primera mascota", "mascota"),
        ("Tu escuela primaria", "escuela"),
        ("Ciudad natal", "ciudad"),
        ("Primer amor", "amor"),
    ]

    for texto, clave in etiquetas:
        tk.Label(reg_frame, text=texto, bg="#fff3e0").pack()
        entry = tk.Entry(reg_frame, show="*" if clave == "contrasena" else None)
        entry.pack()
        campos[clave] = entry

    def registrar():
        datos = {k: v.get().strip() for k, v in campos.items()}
        if "" in datos.values():
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        exito = registrar_usuario(
            datos["nombre"], datos["usuario"], datos["contrasena"],
            datos["rol"], datos["correo"], datos["fecha"],
            datos["mascota"], datos["escuela"], datos["ciudad"], datos["amor"]
        )
        if exito:
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            mostrar_login()
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

    tk.Button(reg_frame, text="Registrar", bg="#4CAF50", fg="white", command=registrar).pack(padx=10, pady=(20, 10))
    tk.Button(reg_frame, text="Volver al login", bg="#f44336", fg="white", command=mostrar_login).pack(padx=10, pady=(0, 15))

def mostrar_escritorio():
    limpiar_main_frame()

    barra_tareas.pack(side="bottom", fill="x")
    menu_inicio.place_forget()

    # for widget in menu_inicio.winfo_children():
    #     widget.destroy()

    tk.Button(menu_inicio, text="Terminal", width=20, anchor="w", command=lambda: [crear_terminal_contenida(main_frame, barra_tareas), toggle_menu()]).pack(pady=1)
    tk.Button(menu_inicio, text="Calculadora", width=20, anchor="w", command=lambda: [crear_calculadora_contenida(main_frame, barra_tareas), toggle_menu()]).pack(pady=1)
    tk.Button(menu_inicio, text="Bloc de notas (próximamente)", width=20, anchor="w", state="disabled").pack(pady=1)

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

    boton_tarea = tk.Button(barra_tareas, text="Terminal", width=15, relief="sunken", font=("MS Sans Serif", 8), command=lambda: frame_terminal.lift())
    boton_tarea.pack(side="left", padx=2)

    terminal = TerminalSO(salida, frame_terminal, boton_tarea, entrada)

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

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkred", fg="white", bd=0, command=lambda: cerrar_calculadora(frame_calc, boton_tarea))
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

    boton_tarea = tk.Button(barra_tareas, text="Calculadora", width=15, relief="sunken", font=("MS Sans Serif", 8), command=lambda: frame_calc.lift())
    boton_tarea.pack(side="left", padx=2)

    Calculadora(frame_calc, boton_tarea)

def cerrar_calculadora(ventana, boton):
    ventana.destroy()
    boton.destroy()

if __name__ == "__main__":
    asignar_items()
    mostrar_login()
    root.mainloop()
