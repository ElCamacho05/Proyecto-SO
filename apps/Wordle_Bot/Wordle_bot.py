import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from collections import defaultdict
import numpy as np

class WordleSolver:
    def __init__(self, wordle_data):
        self.wordsData = wordle_data
        self.words = wordle_data['word'].tolist()
        self.frequencies = wordle_data['occurrence'].astype(float).tolist()
        total = sum(self.frequencies)
        self.probabilities = [f / total for f in self.frequencies]
        self.letterPositions = self.precalcular_posiciones_letras()
        self.letterFrequencies = self.calcular_frecuencias_letras()
        self.wordScores = self.precalcular_scores_palabras()
        self.mustInclude = set()
        self.mustExclude = set()
        self.positionConstraints = [None] * 5
        self.wrongPositions = [set() for _ in range(5)]

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
            letterScore = sum(self.letterFrequencies[letter] for letter in uniqueLetters) / len(uniqueLetters)
            positionScore = sum(self.letterPositions[letter][i] for i, letter in enumerate(word)) / 5
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

    def filtrar_palabras(self):
        posibles, probs = [], []
        for word, prob in zip(self.words, self.probabilities):
            if any([
                self.positionConstraints[i] is not None and self.positionConstraints[i] != word[i]
                for i in range(5)
            ]):
                continue
            if any([word[i] in self.wrongPositions[i] for i in range(5)]):
                continue
            if not self.mustInclude.issubset(set(word)):
                continue
            if any(l in self.mustExclude for l in word):
                continue
            posibles.append(word)
            probs.append(prob)
        return posibles, probs

    def calcular_score_palabra(self, word, count):
        w = self.wordScores[word]
        weights = (
            {'base': 0.3, 'uniqueness': 0.4, 'letters': 0.2, 'positions': 0.1} if count > 50 else
            {'base': 0.5, 'uniqueness': 0.3, 'letters': 0.1, 'positions': 0.1} if count > 10 else
            {'base': 0.8, 'uniqueness': 0.1, 'letters': 0.05, 'positions': 0.05}
        )
        score = sum(w[k] * weights[k] for k in weights)
        if count > 10 and len(set(word)) < 5:
            score *= (1 - (5 - len(set(word))) * 0.15)
        return score

    def obtener_mejores_palabras(self, n=3):
        posibles, probs = self.filtrar_palabras()
        if not posibles: return []
        if len(posibles) <= n:
            idx = np.argsort(probs)[-n:][::-1]
            return [(posibles[i], probs[i]) for i in idx]
        scored = [(self.calcular_score_palabra(w, len(posibles)) * (1 + self.probabilities[self.words.index(w)] * 2), w) for w in posibles]
        return [(w, s) for s, w in sorted(scored, reverse=True)[:n]]

class WordleSolverApp:
    def __init__(self, master, dataset_path):
        self.master = master
        self.master.configure(bg="white")
        self.wordle_data = pd.read_csv(dataset_path)
        self.solver = WordleSolver(self.wordle_data)
        self.feedbackColors = ['gray'] * 5
        self.guessHistory = []
        self.build_ui()

    def build_ui(self):
        self.master.config(bg="#e0e0e0")
        tk.Label(self.master, text="Wordle Bot", font=("Courier", 18, "bold"), bg="#e0e0e0").pack(pady=10)
        entry_frame = tk.Frame(self.master, bg="#e0e0e0")
        entry_frame.pack()
        tk.Label(entry_frame, text="Palabra:", font=("Courier", 12), bg="#e0e0e0").pack(side="left")
        self.guessEntry = tk.Entry(entry_frame, font=("Courier", 14), width=7)
        self.guessEntry.pack(side="left", padx=5)
        self.colorButtons = []
        for i in range(5):
            btn = tk.Button(entry_frame, text=" ", width=2, bg="lightgray",
                            command=lambda i=i: self.toggle_color(i))
            btn.pack(side="left", padx=2)
            self.colorButtons.append(btn)

        btns = tk.Frame(self.master, bg="#e0e0e0")
        btns.pack(pady=5)
        tk.Button(btns, text="Agregar intento", command=self.agregar_intento).pack(side="left", padx=5)
        tk.Button(btns, text="Reiniciar", command=self.reiniciar).pack(side="left", padx=5)

        self.suggestionLabel = tk.Label(self.master, text="", font=("Courier", 12), bg="#e0e0e0", fg="blue")
        self.suggestionLabel.pack(pady=10)
        self.historyText = tk.Text(self.master, height=8, width=40, bg="white", font=("Courier", 10))
        self.historyText.pack()

    def toggle_color(self, i):
        colors = ['gray', 'yellow', 'green']
        idx = colors.index(self.feedbackColors[i])
        self.feedbackColors[i] = colors[(idx + 1) % 3]
        self.colorButtons[i].config(bg=self.feedbackColors[i])

    def agregar_intento(self):
        guess = self.guessEntry.get().lower()
        if len(guess) != 5 or not guess.isalpha():
            messagebox.showerror("Error", "Debe ser una palabra de 5 letras")
            return
        feedback_map = {'gray': 'B', 'yellow': 'Y', 'green': 'G'}
        feedback = ''.join(feedback_map[c] for c in self.feedbackColors)
        self.solver.actualizar_restricciones(guess, feedback)
        self.guessHistory.append((guess, list(self.feedbackColors)))
        self.update_historial()
        self.feedbackColors = ['gray'] * 5
        for btn in self.colorButtons:
            btn.config(bg="gray")
        self.guessEntry.delete(0, tk.END)
        self.actualizar_sugerencias()

    def actualizar_sugerencias(self):
        mejores = self.solver.obtener_mejores_palabras()
        texto = "\n".join([f"{i+1}. {w.upper()} ({s:.2f})" for i, (w, s) in enumerate(mejores)])
        self.suggestionLabel.config(text=texto)

    def update_historial(self):
        self.historyText.delete("1.0", tk.END)
        for guess, colors in self.guessHistory:
            line = f"{guess.upper()} - " + "".join(
                "■ " if c == 'gray' else "▲ " if c == 'yellow' else "● " for c in colors
            ) + "\n"
            self.historyText.insert(tk.END, line)

    def reiniciar(self):
        self.solver = WordleSolver(self.wordle_data)
        self.feedbackColors = ['gray'] * 5
        self.guessHistory = []
        self.historyText.delete("1.0", tk.END)
        for btn in self.colorButtons:
            btn.config(bg="gray")
        self.suggestionLabel.config(text="")
