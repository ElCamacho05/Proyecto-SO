import tkinter as tk
from tkinter import scrolledtext
import time
from apps.TerminalSO import TerminalSO
from apps.Calculadora import Calculadora
from kernel.usario import registrar_usuario, iniciar_sesion
from tkinter import messagebox
from kernel.Permiso_archivo import tiene_permiso

ventanas_abiertas = []
rol_global = None

def mostrar_login():
    login_win = tk.Tk()
    login_win.title("Login - Tapioca OS")
    login_win.geometry("450x350")
    login_win.configure(bg="#e0f7fa") #color celeste

    tk.Label(login_win, text="Nombre de usuario:", bg="#e0f7fa").pack(pady=5)
    entry_usuario = tk.Entry(login_win)
    entry_usuario.pack()

    tk.Label(login_win, text="Contraseña:", bg="#e0f7fa").pack(pady=5)
    entry_contraseña = tk.Entry(login_win, show="*")
    entry_contraseña.pack()
    def login():
        global rol_global
        usuario = entry_usuario.get()
        contraseña = entry_contraseña.get()
        rol = iniciar_sesion(usuario, contraseña)

        if rol:
            rol_global = rol.lower()
            messagebox.showinfo("Bienvenido", f"Acceso como {rol}")
            login_win.destroy()
            mostrar_escritorio()
        else:
            messagebox.showerror("ERROR, Usuario o contraseña incorrectos")

    def ir_a_registro():
        login_win.destroy()
        mostrar_registro()

    tk.Button(login_win, text="Iniciar sesión", bg="#4CAF50", fg="white",  # Verde
              command=login).pack(padx=10, pady=(10, 5))

    tk.Button(login_win, text="Registrarse", bg="#2196F3", fg="white",  # Azul
              command=ir_a_registro).pack(padx=10, pady=(5, 15))

    login_win.mainloop()

def mostrar_registro():
    reg_win = tk.Tk()
    reg_win.title("Registro - Tapioca OS")
    reg_win.geometry("500x800")
    reg_win.configure(bg="#fff3e0")  # Fondo naranja claro

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
        tk.Label(reg_win, text=texto, bg="#fff3e0").pack()

        entry = tk.Entry(reg_win, show="*" if clave == "contraseña" else None)
        entry.pack()
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
            reg_win.destroy()
            mostrar_login()
        else:
            messagebox.showerror("Error", "El usuario ya existe.")

    tk.Button(reg_win, text="Registrar", bg="#4CAF50", fg="white",  # Verde
              command=registrar).pack(padx=10, pady=(20, 10))

    tk.Button(reg_win, text="Volver al login", bg="#f44336", fg="white",  # Rojo
              command=lambda: [reg_win.destroy(), mostrar_login()]).pack(padx=10, pady=(0, 15))

    reg_win.mainloop()


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
        menu_inicio.place(x=10, y=root.winfo_height() - 160)

def actualizar_reloj():
    reloj.config(text=time.strftime('%H:%M'))
    root.after(60000, actualizar_reloj)

def mostrar_escritorio():
    global root, menu_inicio, barra_tareas, reloj
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

    def abrir_terminal_acceso():
        if tiene_permiso(rol_global, "terminal", "ejecutar"):
            crear_terminal_contenida(root, barra_tareas)
            toggle_menu()
        else:
            messagebox.showwarning("Acceso denegado","No tienes permiso para ingresar")

    tk.Button(menu_inicio, text="Terminal", width=20, anchor="w",
              command=abrir_terminal_acceso).pack(pady=1)
    tk.Button(menu_inicio, text="Calculadora", width=20, anchor="w",
              command=lambda:[crear_calculadora_contenida(root, barra_tareas), toggle_menu()]).pack(pady=1)
    tk.Button(menu_inicio, text="Bloc de notas (próximamente)", width=20, anchor="w", state="disabled").pack(pady=1)

    menu_inicio.place_forget()

    root.mainloop()

if __name__ == "__main__":
    mostrar_login()