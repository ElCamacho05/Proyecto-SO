import tkinter as tk
import random

class SnakeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Juego de la Serpiente")
        self.width = 400
        self.height = 400
        self.cell_size = 20
        self.direction = 'Right'
        self.running = True

        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.reset_game()
        self.master.bind("<Key>", self.change_direction)
        self.game_loop()

    def reset_game(self):
        self.snake_positions = [(100, 100), (80, 100), (60, 100)]
        self.food_position = self.set_new_food_position()
        self.score = 0
        self.direction = 'Right'
        self.running = True

    def set_new_food_position(self):
        while True:
            x = random.randint(0, (self.width - self.cell_size) // self.cell_size) * self.cell_size
            y = random.randint(0, (self.height - self.cell_size) // self.cell_size) * self.cell_size
            if (x, y) not in self.snake_positions:
                return (x, y)

    def change_direction(self, event):
        new_direction = event.keysym
        all_directions = ['Up', 'Down', 'Left', 'Right']
        opposites = {'Up':'Down', 'Down':'Up', 'Left':'Right', 'Right':'Left'}

        if new_direction in all_directions:
            if new_direction != opposites.get(self.direction):
                self.direction = new_direction

    def move_snake(self):
        head_x, head_y = self.snake_positions[0]

        if self.direction == 'Up':
            new_head = (head_x, head_y - self.cell_size)
        elif self.direction == 'Down':
            new_head = (head_x, head_y + self.cell_size)
        elif self.direction == 'Left':
            new_head = (head_x - self.cell_size, head_y)
        elif self.direction == 'Right':
            new_head = (head_x + self.cell_size, head_y)

        # Check collisions
        if (new_head in self.snake_positions or
            new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.running = False
            return

        self.snake_positions = [new_head] + self.snake_positions[:-1]

        # Check if food eaten
        if new_head == self.food_position:
            self.snake_positions.append(self.snake_positions[-1])
            self.score += 1
            self.food_position = self.set_new_food_position()

    def draw_elements(self):
        self.canvas.delete("all")

        # Draw food
        x, y = self.food_position
        self.canvas.create_oval(x, y, x + self.cell_size, y + self.cell_size, fill='red', outline='')

        # Draw snake
        for i, (x, y) in enumerate(self.snake_positions):
            color = 'green' if i == 0 else 'lightgreen'
            self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=color, outline='')

        # Draw score
        self.canvas.create_text(50, 10, text=f"Puntaje: {self.score}", fill="white", font=("Arial", 14))

    def game_loop(self):
        if self.running:
            self.move_snake()
            self.draw_elements()
            self.master.after(100, self.game_loop)
        else:
            self.canvas.create_text(self.width//2, self.height//2,
                                    text="Fin del juego!\nPresiona R para reiniciar",
                                    fill="white", font=("Arial", 20))
            self.master.bind("r", self.restart_game)

    def restart_game(self, event):
        self.reset_game()
        self.master.unbind("r")
        self.game_loop()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
