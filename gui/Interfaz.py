# interfaz.py

import tkinter as tk
from tkinter import scrolledtext
import time
from apps.TerminalSO import TerminalSO
from apps.Calculadora import Calculadora
from apps.snake import SnakeGame
from apps.FlappyBird import FlappyBirdGame  # importa la clase de tu juego
from apps.TutorialesTapioka import TutorialesTapioka
from apps.Wordle_Bot.Wordle_bot import WordleSolverApp
from apps.RedSocial.Servidor import ForoChatApp
from kernel.usario import registrar_usuario, iniciar_sesion
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import hashlib
import platform
import tempfile
import subprocess
import pygame
pygame.mixer.init()
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
# --- Íconos de apps en escritorio ---
iconos_apps = []  # para mantener referencias y evitar GC
# ================== VENTANA PRINCIPAL =====================
ventanas_abiertas = []
ventana = tk.Tk()
ventana.title("Tapioka OS")
ventana.config(bg=PALETA['fondo'])
# Pantalla completa según el sistema operativo
if platform.system() == "Windows":
    ventana.state('zoomed')
else:  # Linux, macOS
    ventana.attributes('-zoomed', True)

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

def reproducir_musica_fondo(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play(-1)  # -1 = Bucle infinito

def detener_musica_fondo():
    pygame.mixer.music.stop()

def sonido_click():
    pygame.mixer.Sound("../Assets/click.mp3").play()

def limpiar_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()
# ================== FUNCIONES =====================
def mostrar_login():
    limpiar_frame()

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
              command=lambda:[sonido_click(), login()]).pack(pady=15)

    tk.Button(main_frame, text="Registrarse", font=FUENTE_NORMAL, bg=PALETA['barra'], fg=PALETA['texto'],
              command=lambda:[sonido_click(), mostrar_registro()]).pack(pady=5)

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
            command=lambda:[sonido_click(),registrar()]).pack(pady=15)

    tk.Button(main_frame, text="Volver", font=FUENTE_NORMAL, bg=PALETA['barra'], fg=PALETA['texto'],
            command=lambda:[sonido_click(),mostrar_login()]).pack()

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

def crear_snake_contenida(contenedor, barra_tareas):
    frame_snake = tk.Frame(contenedor, bg="gray", bd=2, relief="raised")
    frame_snake.place(x=300, y=150, width=400, height=400)  # Ancho y alto un poco mayor que el canvas
    ventanas_abiertas.append(frame_snake)

    barra = tk.Frame(frame_snake, bg="darkgreen", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="Snake - Tapioka OS", bg="darkgreen", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkgreen", fg="white", bd=0,
                             command=lambda: cerrar_snake(frame_snake, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        frame_snake.startX = event.x_root - frame_snake.winfo_rootx()
        frame_snake.startY = event.y_root - frame_snake.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - frame_snake.startX
        y = event.y_root - frame_snake.startY
        frame_snake.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="Snake", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_snake.lift())
    boton_tarea.pack(side="left", padx=2)

    # Crear instancia de SnakeGame con el frame_snake como master
    juego = SnakeGame(frame_snake)

    # Pedir foco para que reciba eventos de teclado
    frame_snake.focus_set()

    # También, cada vez que se levante el frame, darle foco para capturar teclas
    def on_lift(event):
        frame_snake.focus_set()

    frame_snake.bind("<Map>", on_lift)  # Cuando se muestra/levanta el frame

    return juego

def cerrar_snake(ventana, boton):
    ventana.destroy()
    boton.destroy()

def crear_flappybird_contenida(contenedor, barra_tareas):
    frame_flappy = tk.Frame(contenedor, bg="black", bd=2, relief="raised")
    frame_flappy.place(x=300, y=150, width=800, height=600)
    ventanas_abiertas.append(frame_flappy)

    barra = tk.Frame(frame_flappy, bg="darkblue", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="Flappy Bird - Tapioka OS", bg="darkblue", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkblue", fg="white", bd=0,
                             command=lambda: cerrar_ventana_flappy(frame_flappy, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        frame_flappy.startX = event.x_root - frame_flappy.winfo_rootx()
        frame_flappy.startY = event.y_root - frame_flappy.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - frame_flappy.startX
        y = event.y_root - frame_flappy.startY
        frame_flappy.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="Flappy Bird", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_flappy.lift())
    boton_tarea.pack(side="left", padx=2)

    # Crear la instancia del juego FlappyBird dentro del frame
    juego_flappy = FlappyBirdGame(frame_flappy)

    # Dar foco al frame para capturar teclado
    frame_flappy.focus_set()

    # También darle foco cada vez que se levanta
    def on_lift(event):
        frame_flappy.focus_set()

    frame_flappy.bind("<Map>", on_lift)

    return juego_flappy

def cerrar_ventana_flappy(ventana, boton):
    ventana.destroy()
    boton.destroy()

def crear_ide_tapioka_contenida(contenedor, barra_tareas):
    frame_ide = tk.Frame(contenedor, bg="black", bd=2, relief="raised")
    frame_ide.place(x=200, y=100, width=900, height=800)
    ventanas_abiertas.append(frame_ide)

    barra = tk.Frame(frame_ide, bg="darkgreen", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="BubbleIDE", bg="darkgreen", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkgreen", fg="white", bd=0,
                             command=lambda: cerrar_ventana_ide(frame_ide, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        frame_ide.startX = event.x_root - frame_ide.winfo_rootx()
        frame_ide.startY = event.y_root - frame_ide.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - frame_ide.startX
        y = event.y_root - frame_ide.startY
        frame_ide.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="IDE C", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_ide.lift())
    boton_tarea.pack(side="left", padx=2)

    # Campo para escribir código C
    editor = tk.Text(frame_ide, bg="black", fg="lime", insertbackground="white", font=("Courier", 18))
    editor.place(x=5, y=30, width=880, height=450)

    # Área de salida
    salida = tk.Text(frame_ide, bg="black", fg="cyan", font=("Courier", 16))
    salida.place(x=5, y=490, width=880, height=270)

    # Botón para compilar
    def compilar_y_ejecutar():
        codigo_c = editor.get("1.0", tk.END)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as temp_c:
            temp_c.write(codigo_c.encode("utf-8"))
            temp_c.close()
            nombre_binario = temp_c.name.replace(".c", "")

            try:
                resultado = subprocess.run(["gcc", temp_c.name, "-o", nombre_binario], capture_output=True, text=True)
                if resultado.returncode != 0:
                    salida.insert(tk.END, "❌ Error de compilación:\n" + resultado.stderr + "\n")
                else:
                    salida.insert(tk.END, "✅ Compilación exitosa. Ejecutando...\n")
                    ejecucion = subprocess.run([nombre_binario], capture_output=True, text=True)
                    salida.insert(tk.END, ejecucion.stdout + "\n")
                    if ejecucion.stderr:
                        salida.insert(tk.END, "⚠️ Errores:\n" + ejecucion.stderr + "\n")
            except Exception as e:
                salida.insert(tk.END, f"Error: {e}\n")

    boton_compilar = tk.Button(frame_ide, text="Compilar & Ejecutar", bg="darkgreen", fg="white",
                               command=compilar_y_ejecutar)
    boton_compilar.place(x=120, y=770)

def cerrar_ventana_ide(ventana, boton):
    ventana.destroy()
    boton.destroy()

def crear_tutoriales_tapioka_contenida(contenedor, barra_tareas):
    frame_tutoriales = tk.Frame(contenedor, bg="black", bd=2, relief="raised")
    frame_tutoriales.place(x=100, y=80, width=900, height=600)
    ventanas_abiertas.append(frame_tutoriales)

    barra = tk.Frame(frame_tutoriales, bg="darkblue", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="Tutoriales Tapioka", bg="darkblue", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkblue", fg="white", bd=0,
                             command=lambda: cerrar_ventana_tutoriales(frame_tutoriales, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        frame_tutoriales.startX = event.x_root - frame_tutoriales.winfo_rootx()
        frame_tutoriales.startY = event.y_root - frame_tutoriales.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - frame_tutoriales.startX
        y = event.y_root - frame_tutoriales.startY
        frame_tutoriales.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="Tutoriales", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_tutoriales.lift())
    boton_tarea.pack(side="left", padx=2)

    TutorialesTapioka(frame_tutoriales, "../apps/tutoriales.json")

def cerrar_ventana_tutoriales(ventana, boton):
    ventana.destroy()
    boton.destroy()

def crear_wordlebot_contenida(contenedor, barra_tareas):
    frame_wordle = tk.Frame(contenedor, bg="black", bd=2, relief="raised")
    frame_wordle.place(x=300, y=100, width=450, height=520)
    ventanas_abiertas.append(frame_wordle)

    barra = tk.Frame(frame_wordle, bg="darkred", height=25)
    barra.pack(fill="x")

    titulo = tk.Label(barra, text="Wordle Bot - Tapioka", bg="darkred", fg="white", font=("MS Sans Serif", 9))
    titulo.pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkred", fg="white", bd=0,
                             command=lambda: cerrar_ventana_wordle(frame_wordle, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        frame_wordle.startX = event.x_root - frame_wordle.winfo_rootx()
        frame_wordle.startY = event.y_root - frame_wordle.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - frame_wordle.startX
        y = event.y_root - frame_wordle.startY
        frame_wordle.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="Wordle Bot", width=15, relief="sunken", font=("MS Sans Serif", 8),
                            command=lambda: frame_wordle.lift())
    boton_tarea.pack(side="left", padx=2)

    # Aquí instanciamos el bot con su dataset
    app = WordleSolverApp(frame_wordle, "../apps/Wordle_Bot/wordle.csv")

def cerrar_ventana_wordle(ventana, boton):
    ventana.destroy()
    boton.destroy()

def crear_forochat_contenida(contenedor, barra_tareas):
    ventana = tk.Frame(contenedor, bg="black", bd=2, relief="raised")
    ventana.place(x=250, y=90, width=500, height=550)
    ventanas_abiertas.append(ventana)

    barra = tk.Frame(ventana, bg="darkblue", height=25)
    barra.pack(fill="x")
    tk.Label(barra, text="Foro Chat - Tapioka", bg="darkblue", fg="white", font=("MS Sans Serif", 9)).pack(side="left", padx=5)

    boton_cerrar = tk.Button(barra, text="X", font=("MS Sans Serif", 9, "bold"), bg="darkblue", fg="white", bd=0,
                             command=lambda: cerrar_ventana_forochat(ventana, boton_tarea))
    boton_cerrar.pack(side="right", padx=5)

    def iniciar_movimiento(event):
        ventana.startX = event.x_root - ventana.winfo_rootx()
        ventana.startY = event.y_root - ventana.winfo_rooty()

    def mover_ventana(event):
        x = event.x_root - ventana.startX
        y = event.x_root - ventana.startY
        ventana.place(x=x, y=y)

    barra.bind("<Button-1>", iniciar_movimiento)
    barra.bind("<B1-Motion>", mover_ventana)

    boton_tarea = tk.Button(barra_tareas, text="Foro Chat", width=15, relief="sunken",
                            font=("MS Sans Serif", 8), command=lambda: ventana.lift())
    boton_tarea.pack(side="left", padx=2)

    ForoChatApp(ventana)

def cerrar_ventana_forochat(ventana, boton):
    ventana.destroy()
    boton.destroy()

def toggle_menu():
    if menu_inicio.winfo_ismapped():
        menu_inicio.place_forget()
    else:
        menu_inicio.place(x=10, y=escritorio.winfo_height() - 120)

def actualizar_reloj():
    reloj.config(text=time.strftime('%H:%M'))
    escritorio.after(60000, actualizar_reloj)

def mostrar_escritorio():
    limpiar_frame()
    detener_musica_fondo()

    global escritorio, reloj, menu_inicio,fondo_escritorio_tk

    escritorio = tk.Frame(canvas, bg=PALETA['ventana'], bd=4, relief="ridge")
    escritorio.pack(expand=True, fill="both")

    # Carga y coloca la imagen de fondo en escritorio
    fondo_escritorio_img = Image.open("../Assets/escritorio.jpg")  # Ruta a tu imagen
    fondo_escritorio_tk = ImageTk.PhotoImage(fondo_escritorio_img)
    fondo_label = tk.Label(escritorio, image=fondo_escritorio_tk)
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

    barra_tareas = tk.Frame(escritorio, bg=PALETA['texto'], height=60, bd=2, relief="raised")
    barra_tareas.pack(side="bottom", fill="x")

    boton_inicio = tk.Button(barra_tareas, text="Inicio", font=("MS Sans Serif", 10, "bold"),
                             bg=PALETA['texto'],anchor="e", fg="white", command=lambda:[sonido_click(),toggle_menu()])
    boton_inicio.pack(side="left", padx=5)

    reloj = tk.Label(barra_tareas, text="", font=("MS Sans Serif", 9), bg=PALETA['texto'], fg="white", anchor="e")
    reloj.pack(side="right", padx=10)
    actualizar_reloj()

    menu_inicio = tk.Frame(escritorio, bg=PALETA['texto'], bd=2)

    tk.Button(menu_inicio, text="Terminal",bg=PALETA['texto'], width=20, anchor="w", fg="white",
              command=lambda:[sonido_click(),crear_terminal_contenida(escritorio, barra_tareas), toggle_menu()]).pack(pady=1)
    tk.Button(menu_inicio, text="Calculadora",bg=PALETA['texto'], width=20, anchor="w", fg="white",
              command=lambda:[sonido_click(),crear_calculadora_contenida(escritorio, barra_tareas), toggle_menu()]).pack(pady=1)

    def crear_icono_app(nombre, ruta_imagen, comando, x, y):
        try:
            tamaño_icono = (128, 128)  # Aumentado el tamaño
            img = Image.open(ruta_imagen).convert("RGBA").resize(tamaño_icono, Image.Resampling.LANCZOS)

            # Rellenar transparencia con negro
            fondo_negro = Image.new("RGBA", img.size, (22, 24, 22, 255))
            img = Image.alpha_composite(fondo_negro, img)

            img_tk = ImageTk.PhotoImage(img)  # No lo conviertas a RGB, Tkinter ya lo acepta como RGBA
            iconos_apps.append(img_tk)  # Mantener referencia global

            boton = tk.Button(escritorio, image=img_tk, text=nombre, compound="top",
                              fg="white", bg="#161816", activebackground="black",
                              activeforeground="white", font=("Courier New", 10),
                              borderwidth=0, highlightthickness=0,
                              command=lambda: [sonido_click(), comando()])
            boton.place(x=x, y=y)

        except Exception as e:
            print(f"Error cargando imagen '{ruta_imagen}': {e}")

    # Agrega tus apps aquí con sus rutas de iconos y funciones
    crear_icono_app("Terminal", "../Assets/terminal.png",
                    lambda: crear_terminal_contenida(escritorio, barra_tareas), 50, 50)
    crear_icono_app("Calculadora", "../Assets/calcular.png",
                    lambda: crear_calculadora_contenida(escritorio, barra_tareas), 250, 50)
    crear_icono_app("Snake", "../Assets/snake.png",
                    lambda: crear_snake_contenida(escritorio, barra_tareas), 450, 50)
    crear_icono_app("Flappy Bird", "../Assets/bird.png",
                    lambda: crear_flappybird_contenida(escritorio, barra_tareas), 650, 50)
    crear_icono_app("BubbleIDE", "../Assets/ide.png",
                    lambda: crear_ide_tapioka_contenida(escritorio, barra_tareas), 850, 50)
    crear_icono_app("Tutoriales Tapioka", "../Assets/tutoriales.png",
                    lambda: crear_tutoriales_tapioka_contenida(escritorio, barra_tareas),1050, 50)
    crear_icono_app("Wordle Bot", "../Assets/wordle.png",
                    lambda: crear_wordlebot_contenida(escritorio, barra_tareas), 50, 300)
    crear_icono_app("Foro Chat", "../Assets/mensajes.png",
                    lambda: crear_forochat_contenida(escritorio, barra_tareas), x=250, y=300)


if __name__ == "__main__":
    reproducir_musica_fondo("../Assets/musica.mp3")  # Ruta a tu canción en bucle
    mostrar_login()
    #mostrar_escritorio()
    ventana.mainloop()