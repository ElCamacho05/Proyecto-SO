import tkinter as tk
import json

class TutorialesTapioka:
    def __init__(self, master, json_path):
        self.master = master
        self.json_path = json_path

        self.secciones = self.cargar_tutoriales()

        # Frame del contenido con scroll
        self.text_frame = tk.Frame(master, bg="black")
        self.text_frame.pack(expand=True, fill="both")

        self.text_area = tk.Text(self.text_frame, wrap="word", bg="black", fg="white",
                                 insertbackground="white", font=("Courier", 16))
        self.text_area.pack(side="left", expand=True, fill="both")

        scroll = tk.Scrollbar(self.text_frame, command=self.text_area.yview)
        scroll.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scroll.set)

        # Frame de botones
        self.botones_frame = tk.Frame(master, bg="darkblue")
        self.botones_frame.pack(fill="x")

        # Botón para regresar al índice
        boton_indice = tk.Button(self.botones_frame, text="🏠 Índice", bg="darkblue", fg="white",
                                 command=self.mostrar_indice)
        boton_indice.pack(side="left", padx=5, pady=2)

        self.mostrar_indice()

    def cargar_tutoriales(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            return {"Error": [f"No se pudo cargar el archivo: {e}"]}

    def mostrar_indice(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "Te damos la bienvenida a Tapioka - Tutoriales 📚\n\n")
        self.text_area.insert(tk.END, "¿Preparad@ para aprender C?\n\n")
        for titulo in self.secciones.keys():
            self.text_area.insert(tk.END, f"👉 {titulo}\n")
        self.text_area.insert(tk.END, "\nHaz clic en un título para leerlo.\n")

        # Añadir eventos clicables
        for titulo in self.secciones.keys():
            self.text_area.insert(tk.END, f"\n")
            self.text_area.window_create(tk.END, window=tk.Button(self.text_area, text=titulo, bg="black", fg="cyan",
                                                                  font=("Courier", 14),
                                                                  command=lambda t=titulo: self.mostrar_tutorial(t)))

    def mostrar_tutorial(self, titulo):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, f"{titulo}\n\n", "titulo")
        contenido = self.secciones.get(titulo, ["No disponible"])
        for parrafo in contenido:
            self.text_area.insert(tk.END, parrafo + "\n\n")

        self.text_area.tag_configure("titulo", font=("MS Sans Serif", 20, "bold"), foreground="cyan")

        # Mostrar botón de volver al índice en la parte inferior también
        self.text_area.insert(tk.END, "\n")
        self.text_area.window_create(tk.END, window=tk.Button(self.text_area, text="🔙 Volver al Índice",
                                                              bg="darkblue", fg="white", font=("Courier", 12, "bold"),
                                                              command=self.mostrar_indice))

