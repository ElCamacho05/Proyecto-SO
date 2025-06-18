# Haziel Lopez Castillo
# Bot para resolver el juego Wordle

import tkinter as tk
from tkinter import ttk, messagebox
# Espero este bien usar esta parte
import pandas as pd
from collections import defaultdict
import numpy as np #numpy

# Una GUI sencilla
class WordleSolverGUI:
    def __init__(self, master, wordle_data):
        self.master = master
        master.title("Wordle Bot 🤖") # Queria poner mas emojis pero no me dejo el tkinter
        master.configure(bg='#f0f0f0')
        
        self.style = ttk.Style()
        self.style.configure('TFrame', background="#fefefe")
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 14))
        self.style.configure('TButton', font=('Helvetica', 14), padding=5)
        self.style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'))
        self.style.configure('Suggestion.TLabel', font=('Helvetica', 12))
        
        self.solver = WordleSolver(wordle_data)
        
        self.currentGuess = ""
        self.feedbackColors = ['gray'] * 5 # Grande python por dejarme multiplicar cosas asi
        self.guessHistory = []
        
        self.crear_widgets()

    def crear_widgets(self):
        mainFrame = ttk.Frame(self.master, padding="20")
        mainFrame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        for i in range(6):
            mainFrame.columnconfigure(i, weight=1)
        
        ttk.Label(mainFrame, text="Wordle Bot", style='Title.TLabel').grid(
            row=0, column=0, columnspan=6, pady=(0, 20))
        
        ttk.Label(mainFrame, text="Última palabra usada:").grid(
            row=1, column=0, sticky=tk.E, padx=5)
        
        self.guessEntry = ttk.Entry(mainFrame, width=12, font=('Helvetica', 14))
        self.guessEntry.grid(row=1, column=1, columnspan=3, sticky=tk.W)
        
        colorFrame = ttk.Frame(mainFrame)
        colorFrame.grid(row=2, column=0, columnspan=6, pady=10)
        
        self.colorButtons = []
        for i in range(5):
            btn = tk.Button(
                colorFrame, 
                text=" ", 
                bg='light gray', 
                width=4, 
                height=2,
                relief='flat',
                activebackground='light gray',
                font=('Helvetica', 12),
                command=lambda idx=i: self.ciclar_color(idx)
            )
            btn.grid(row=0, column=i, padx=3)
            btn.bind("<Enter>", lambda e, b=btn: self.al_pasar_sobre_boton(b))
            btn.bind("<Leave>", lambda e, b=btn: self.al_salir_de_boton(b))
            self.colorButtons.append(btn)
        
        ttk.Button(mainFrame, text="Agregar Intento", command=self.agregar_intento).grid(
            row=3, column=0, columnspan=3, pady=10, sticky='ew')
            
        ttk.Button(mainFrame, text="Reiniciar", command=self.reiniciar_solver).grid(
            row=3, column=3, columnspan=3, pady=10, sticky='ew')
        
        ttk.Separator(mainFrame, orient='horizontal').grid(
            row=4, column=0, columnspan=6, pady=10, sticky='ew')
        
        ttk.Label(mainFrame, text="Top 3 mejores sugerencias:").grid(
            row=5, column=0, columnspan=6, sticky=tk.W, pady=(5, 0))
        
        self.suggestionLabel = ttk.Label(
            mainFrame, 
            text="", 
            style='Suggestion.TLabel',
            foreground='#2c7be5'
        )
        self.suggestionLabel.grid(row=6, column=0, columnspan=6, sticky=tk.W)
        
        self.scoreLabel = ttk.Label(
            mainFrame, 
            text="", 
            style='TLabel',
            foreground='#6c757d'
        )
        self.scoreLabel.grid(row=7, column=0, columnspan=6, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(mainFrame, text="Historial:").grid(
            row=8, column=0, columnspan=6, sticky=tk.W, pady=(5, 0))
        
        self.historyText = tk.Text(
            mainFrame, 
            height=6, 
            width=40, 
            state='disabled',
            bg='white',
            bd=2,
            relief='groove',
            padx=5,
            pady=5,
            wrap=tk.WORD,
            font=('Helvetica', 12)
        )
        self.historyText.grid(row=9, column=0, columnspan=6, sticky='ew')
        
        self.actualizar_sugerencias()
        self.master.geometry("380x550")          
        self.master.resizable(False, False)
    
    def al_pasar_sobre_boton(self, button): # El Hover
        pass
    
    def al_salir_de_boton(self, button): # Salir del boton
        pass
    
    # Esto me costo por alguna razon
    def ciclar_color(self, index):
        colors = ['gray', 'yellow', 'green']
        currentColor = self.feedbackColors[index]
        nextColor = colors[(colors.index(currentColor) + 1) % len(colors)]
        self.feedbackColors[index] = nextColor
        self.colorButtons[index].config(bg=nextColor)
    
    # Aqui es para agregar un intento para resolver el Wordle 
    # Tambien para evitar errores de capa 8, los anuncios   
    def agregar_intento(self):
        guess = self.guessEntry.get().lower()
        if len(guess) != 5:
            messagebox.showerror("Error", "La palabra debe tener exactamente 5 letras")
            return
        
        if not guess.isalpha():
            messagebox.showerror("Error", "Solo se permiten letras (A-Z)")
            return
        
        colorToFeedback = {'gray': 'B', 'yellow': 'Y', 'green': 'G'}
        feedback = ''.join([colorToFeedback[color] for color in self.feedbackColors])
        
        self.solver.actualizar_restricciones(guess, feedback)
        self.guessHistory.append((guess, self.feedbackColors.copy()))
        self.actualizar_historial()
        
        self.guessEntry.delete(0, tk.END)
        self.feedbackColors = ['gray'] * 5
        for btn in self.colorButtons:
            btn.config(bg='light gray')
        
        self.actualizar_sugerencias()
    
    # Esto nomas por que es mas comodo reiniciar que apagar y prender
    def reiniciar_solver(self):
        self.solver = WordleSolver(self.solver.wordsData)
        self.guessHistory = []
        self.feedbackColors = ['gray'] * 5
        self.guessEntry.delete(0, tk.END)
        for btn in self.colorButtons:
            btn.config(bg='light gray')
        self.actualizar_historial()
        self.actualizar_sugerencias()
        messagebox.showinfo("Reiniciado", "El Bot ha sido reiniciado.")
    
    # Aqui agregamos a el historial de intentos
    def actualizar_historial(self):
        self.historyText.config(state='normal')
        self.historyText.delete(1.0, tk.END)
        
        for guess, colors in self.guessHistory:
            self.historyText.insert(tk.END, f"{guess.upper()} - ")
            for color in colors:
                char = "■ " if color == 'gray' else "▲ " if color == 'yellow' else "● "
                self.historyText.insert(tk.END, char)
            self.historyText.insert(tk.END, "\n")
        
        self.historyText.config(state='disabled')
    
    # Aqui actualizamos las sugerencias que nos da la Heuristica
    def actualizar_sugerencias(self):
        suggestions = self.solver.obtener_mejores_palabras(3)
        
        if suggestions:
            suggestionText = "\n".join(
                [f"{i+1}. {word.upper()} (Score: {score:.2f})" 
                for i, (word, score) in enumerate(suggestions) if isinstance(word, str)]
            )
            self.suggestionLabel.config(text=suggestionText)
            
            # Para que se vea que se esta calificando
            # Aqui queria poner los emojis pero no me dejo y ya no quise buscar
            reglas = (
                "Puntuación basada en:\n"
                "- Frecuencia de letras/posiciones\n"
                "- Letras Únicas\n"
                "- Probabilidad Por Palabra"
            )
            self.scoreLabel.config(text=reglas)
        else:
            self.suggestionLabel.config(text="No hay palabras posibles")
            self.scoreLabel.config(text="")

# La clase solver, el bueno
class WordleSolver:
    def __init__(self, wordle_data):
        self.wordsData = wordle_data
        self.words = wordle_data['word'].tolist()
        self.frequencies = wordle_data['occurrence'].astype(float).tolist()
        
        total = sum(self.frequencies)
        self.probabilities = [f/total for f in self.frequencies]
        
        self.letterPositions = self.precalcular_posiciones_letras()
        self.letterFrequencies = self.calcular_frecuencias_letras()
        self.wordScores = self.precalcular_scores_palabras()
        
        self.mustInclude = set()
        self.mustExclude = set()
        self.positionConstraints = [None]*5
        self.wrongPositions = [set() for _ in range(5)]
        
    # Estas funciones son para manejar y precargar datos antes de empezar
    def precalcular_posiciones_letras(self):
        letterPos = defaultdict(lambda: defaultdict(float))
        for word, prob in zip(self.words, self.probabilities):
            for i, letter in enumerate(word):
                letterPos[letter][i] += prob * 1000
        return letterPos
    
    def calcular_frecuencias_letras(self):
        freq = defaultdict(float)
        for word, prob in zip(self.words, self.probabilities):
            for letter in set(word):
                freq[letter] += prob
        return freq
    
    def precalcular_scores_palabras(self):
        wordScores = {}
        maxFreq = max(self.frequencies)
        
        for word, freq in zip(self.words, self.frequencies):
            baseScore = freq / maxFreq
            uniqueLetters = set(word)
            uniqueness = len(uniqueLetters) / 5
            letterScore = sum(self.letterFrequencies[letter] for letter in uniqueLetters)
            letterScore /= len(uniqueLetters)
            
            positionScore = 0
            for i, letter in enumerate(word):
                positionScore += self.letterPositions[letter][i]
            positionScore /= 5
            
            wordScores[word] = {
                'base': baseScore,
                'uniqueness': uniqueness,
                'letters': letterScore,
                'positions': positionScore
            }
        
        return wordScores
    
    def actualizar_restricciones(self, guess, feedback):
        for i, (letter, fb) in enumerate(zip(guess, feedback)):
            if fb == 'G':
                self.positionConstraints[i] = letter
                self.mustInclude.add(letter)
            elif fb == 'Y':
                self.mustInclude.add(letter)
                self.wrongPositions[i].add(letter)
            elif fb == 'B':
                if letter not in self.mustInclude:
                    self.mustExclude.add(letter)
    
    # Esto es lo importante, filtrar las palabras
    def filtrar_palabras(self):
        possibleWords = []
        possibleProbs = []
        
        for word, prob in zip(self.words, self.probabilities):
            valid = True
            for i, (constraint, letter) in enumerate(zip(self.positionConstraints, word)):
                if constraint is not None and constraint != letter:
                    valid = False
                    break
                if letter in self.wrongPositions[i]:
                    valid = False
                    break
            
            if not valid:
                continue
                
            if not self.mustInclude.issubset(set(word)):
                continue
                
            if any(letter in self.mustExclude for letter in word):
                continue
                
            possibleWords.append(word)
            possibleProbs.append(prob)
        
        return possibleWords, possibleProbs
    
    def calcular_score_palabra(self, word, remainingWordsCount):
        wordInfo = self.wordScores[word]

        # Esto lo movi varias veces por que asi al menos puede tener un poco mas de INTENSIDAD
        # Quedo bien
        
        if remainingWordsCount > 50:
            weights = {'base': 0.3, 'uniqueness': 0.4, 'letters': 0.2, 'positions': 0.1}
        elif remainingWordsCount > 10:
            weights = {'base': 0.5, 'uniqueness': 0.3, 'letters': 0.1, 'positions': 0.1}
        else:
            weights = {'base': 0.8, 'uniqueness': 0.1, 'letters': 0.05, 'positions': 0.05}
        
        score = (
            wordInfo['base'] * weights['base'] +
            wordInfo['uniqueness'] * weights['uniqueness'] +
            wordInfo['letters'] * weights['letters'] +
            wordInfo['positions'] * weights['positions']
        )
        
        if remainingWordsCount > 10 and len(set(word)) < 5:
            penalty = (5 - len(set(word))) * 0.15
            score *= (1 - penalty)
        
        return score
    
    # Las mejores palabras y solo las mejores palabras, asies.
    def obtener_mejores_palabras(self, n=3):
        possibleWords, possibleProbs = self.filtrar_palabras()
        
        if not possibleWords:
            return []
        
        remainingCount = len(possibleWords)
        
        if remainingCount <= n:
            indices = np.argsort(possibleProbs)[-n:][::-1]
            return [(str(possibleWords[i]), float(possibleProbs[i])) for i in indices]
        
        scoredWords = []
        for word in possibleWords:
            score = self.calcular_score_palabra(word, remainingCount)
            wordProb = self.probabilities[self.words.index(word)]
            adjustedScore = score * (1 + wordProb * 2)
            scoredWords.append((float(adjustedScore), str(word)))
        
        scoredWords.sort(reverse=True, key=lambda x: x[0])
        
        if remainingCount > 30:
            topWords = scoredWords[:10]
            topWords.sort(reverse=True, key=lambda x: (len(set(x[1])), x[0]))
            return [(word, score) for score, word in topWords[:n]]
        
        return [(word, score) for score, word in scoredWords[:n]]

# Esto es de donde viene el dataset, para que funcione debe estar todo dentro de la capeta del zip
wordle_data = pd.read_csv('Wordle_Bot/wordle.csv')
root = tk.Tk()
app = WordleSolverGUI(root, wordle_data)
root.mainloop()

# Y hasta aca, espero este bien el programa.


