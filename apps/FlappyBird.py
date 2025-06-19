import pygame
import sys
import random

def iniciar_flappybird():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    GRAVITY = 0.4
    JUMP = -8
    SPEED = 4
    GAP = 150
    OBSTACLE_WIDTH = 80
    AZUL_CLARO = (135, 206, 250)
    VERDE = (0, 255, 0)
    NEGRO = (0, 0, 0)
    AMARILLO = (255, 255, 0)

    bird_y = HEIGHT // 2
    bird_vel = 0
    score = 0
    lives = 3
    game_over = False

    def generate_obstacle(x):
        altura_inf = random.randint(100, HEIGHT - GAP - 100)
        return {"x": x, "altura_inf": altura_inf, "puntuado": False}

    obstacles = [generate_obstacle(x * 300 + WIDTH) for x in range(3)]

    def check_collision():
        bird_rect = pygame.Rect(100 - 20, bird_y - 20, 40, 40)
        for ob in obstacles:
            top_rect = pygame.Rect(ob["x"], 0, OBSTACLE_WIDTH, ob["altura_inf"])
            bottom_rect = pygame.Rect(ob["x"], ob["altura_inf"] + GAP, OBSTACLE_WIDTH, HEIGHT)
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True
        if bird_y < 0 or bird_y > HEIGHT:
            return True
        return False

    def draw_text(text, x, y, size=36, center=False):
        fuente = pygame.font.SysFont(None, size)
        render = fuente.render(text, True, NEGRO)
        rect = render.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        win.blit(render, rect)

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_UP:
                        bird_vel = JUMP
                if event.key == pygame.K_r and game_over:
                    bird_y = HEIGHT // 2
                    bird_vel = 0
                    score = 0
                    lives = 3
                    game_over = False
                    obstacles = [generate_obstacle(x * 300 + WIDTH) for x in range(3)]

        if not game_over:
            bird_vel += GRAVITY
            bird_y += bird_vel

            for ob in obstacles:
                ob["x"] -= SPEED
                if not ob["puntuado"] and ob["x"] + OBSTACLE_WIDTH < 100:
                    score += 1
                    ob["puntuado"] = True
                if ob["x"] + OBSTACLE_WIDTH < 0:
                    obstacles.remove(ob)
                    obstacles.append(generate_obstacle(WIDTH + 100))

            if check_collision():
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    bird_y = HEIGHT // 2
                    bird_vel = 0

        win.fill(AZUL_CLARO)
        pygame.draw.circle(win, AMARILLO, (100, int(bird_y)), 20)

        for ob in obstacles:
            pygame.draw.rect(win, VERDE, (ob["x"], 0, OBSTACLE_WIDTH, ob["altura_inf"]))
            pygame.draw.rect(win, VERDE, (ob["x"], ob["altura_inf"] + GAP, OBSTACLE_WIDTH, HEIGHT))

        draw_text(f"Puntos: {score}", 10, 10)
        draw_text(f"Vidas: {lives}", 10, 50)

        if game_over:
            draw_text("Juego Terminado", WIDTH // 2, HEIGHT // 2 - 20, 40, center=True)
            draw_text("Presiona R para reiniciar", WIDTH // 2, HEIGHT // 2 + 20, 30, center=True)

        pygame.display.update()
