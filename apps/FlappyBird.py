import tkinter as tk
import os
import pygame
import random

class FlappyBirdGame:
    def __init__(self, master):
        self.master = master
        self.width = 800
        self.height = 600

        self.running = True
        self.pygame_iniciado = False

        # Iniciar pygame después de que Tkinter haya creado el Frame (retraso mínimo)
        self.master.after(100, self.inicializar_pygame)
        self.master.bind("<Key>", self.tk_keydown)

    def inicializar_pygame(self):
        if self.pygame_iniciado:
            return

        os.environ["SDL_WINDOWID"] = str(self.master.winfo_id())
        os.environ["SDL_VIDEODRIVER"] = "x11"

        pygame.display.init()
        pygame.font.init()  # ✅ INICIALIZAR EL MODULO DE FUENTES para evitar el error
        self.win = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        self.pygame_iniciado = True

        self.reset_game()
        self.game_loop()

    def tk_keydown(self, event):
        if event.keysym == "space":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        elif event.keysym == "r":
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))

    def reset_game(self):
        self.GRAVITY = 0.4
        self.JUMP = -8
        self.SPEED = 4
        self.GAP = 150
        self.OBSTACLE_WIDTH = 80

        self.bird_y = self.height // 2
        self.bird_vel = 0
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.obstacles = [self.generate_obstacle(x * 300 + self.width) for x in range(3)]

    def generate_obstacle(self, x):
        altura_inf = random.randint(100, self.height - self.GAP - 100)
        return {"x": x, "altura_inf": altura_inf, "puntuado": False}

    def check_collision(self):
        bird_rect = pygame.Rect(100 - 20, self.bird_y - 20, 40, 40)
        for ob in self.obstacles:
            top_rect = pygame.Rect(ob["x"], 0, self.OBSTACLE_WIDTH, ob["altura_inf"])
            bottom_rect = pygame.Rect(ob["x"], ob["altura_inf"] + self.GAP, self.OBSTACLE_WIDTH, self.height)
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True
        if self.bird_y < 0 or self.bird_y > self.height:
            return True
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.bird_vel = self.JUMP
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def draw_text(self, text, x, y, size=36, center=False):
        render = self.font.render(text, True, (0, 0, 0))
        rect = render.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.win.blit(render, rect)

    def game_loop(self):
        if not self.running:
            pygame.quit()
            return

        self.handle_events()

        if not self.game_over:
            self.bird_vel += self.GRAVITY
            self.bird_y += self.bird_vel

            for ob in self.obstacles:
                ob["x"] -= self.SPEED
                if not ob["puntuado"] and ob["x"] + self.OBSTACLE_WIDTH < 100:
                    self.score += 1
                    ob["puntuado"] = True
                if ob["x"] + self.OBSTACLE_WIDTH < 0:
                    self.obstacles.remove(ob)
                    self.obstacles.append(self.generate_obstacle(self.width + 100))

            if self.check_collision():
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.bird_y = self.height // 2
                    self.bird_vel = 0

        self.win.fill((135, 206, 250))
        pygame.draw.circle(self.win, (255, 255, 0), (100, int(self.bird_y)), 20)

        for ob in self.obstacles:
            pygame.draw.rect(self.win, (0, 255, 0), (ob["x"], 0, self.OBSTACLE_WIDTH, ob["altura_inf"]))
            pygame.draw.rect(self.win, (0, 255, 0), (ob["x"], ob["altura_inf"] + self.GAP, self.OBSTACLE_WIDTH, self.height))

        self.draw_text(f"Puntos: {self.score}", 10, 10)
        self.draw_text(f"Vidas: {self.lives}", 10, 50)

        if self.game_over:
            self.draw_text("Juego Terminado", self.width // 2, self.height // 2 - 20, 40, center=True)
            self.draw_text("Presiona R para reiniciar", self.width // 2, self.height // 2 + 20, 30, center=True)

        pygame.display.update()
        self.master.after(16, self.game_loop)
