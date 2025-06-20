import pygame
import os
import random

class FlappyBirdGame:
    def __init__(self, master):
        self.master = master
        self.width = 800
        self.height = 600

        self.running = True
        self.pygame_iniciado = False

        # Bind para inicializar pygame cuando el frame Tkinter esté visible
        self.master.bind("<Map>", self.inicializar_pygame)

    def tk_keysym_to_pygame(self, keysym):
        mapping = {
            "r": pygame.K_r,
            "space": pygame.K_SPACE,
            "Up": pygame.K_UP,
        }
        return mapping.get(keysym, None)

    def tk_keydown(self, event):
        key = self.tk_keysym_to_pygame(event.keysym)
        if key is not None:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))

    def inicializar_pygame(self, event=None):
        if self.pygame_iniciado:
            return

        # ¡IMPORTANTE! Establece variables ENTORNO ANTES de pygame.init()
        os.environ['SDL_WINDOWID'] = str(self.master.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'x11'  # Solo Linux X11, en Windows eliminar o comentar

        pygame.init()
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Flappy Bird")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        self.reset_game()
        self.pygame_iniciado = True
        self.game_loop()

    def reset_game(self):
        self.GRAVITY = 0.4
        self.JUMP = -8
        self.SPEED = 4
        self.GAP = 150
        self.OBSTACLE_WIDTH = 80

        self.AZUL_CLARO = (135, 206, 250)
        self.VERDE = (0, 255, 0)
        self.NEGRO = (0, 0, 0)
        self.AMARILLO = (255, 255, 0)

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

    def draw_text(self, text, x, y, size=36, center=False):
        fuente = pygame.font.SysFont(None, size)
        render = fuente.render(text, True, self.NEGRO)
        rect = render.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.win.blit(render, rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        self.bird_vel = self.JUMP
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def game_loop(self):
        if not self.running:
            pygame.quit()
            self.master.destroy()
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

        self.win.fill(self.AZUL_CLARO)
        pygame.draw.circle(self.win, self.AMARILLO, (100, int(self.bird_y)), 20)

        for ob in self.obstacles:
            pygame.draw.rect(self.win, self.VERDE, (ob["x"], 0, self.OBSTACLE_WIDTH, ob["altura_inf"]))
            pygame.draw.rect(self.win, self.VERDE, (ob["x"], ob["altura_inf"] + self.GAP, self.OBSTACLE_WIDTH, self.height))

        self.draw_text(f"Puntos: {self.score}", 10, 10)
        self.draw_text(f"Vidas: {self.lives}", 10, 50)

        if self.game_over:
            self.draw_text("Juego Terminado", self.width // 2, self.height // 2 - 20, 40, center=True)
            self.draw_text("Presiona R para reiniciar", self.width // 2, self.height // 2 + 20, 30, center=True)

        pygame.display.update()

        self.master.after(16, self.game_loop)
