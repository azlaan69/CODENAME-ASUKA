import pygame
import sys
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("OH GOD PLEASE WORK IM GOING CRAZY")
clock = pygame.time.Clock()

apple_pos = pygame.math.Vector2(400, 300)
apple_vel = pygame.math.Vector2(0, 0)
snake_pos = pygame.math.Vector2(random.randint(1, 800), random.randint(1, 600))
snake_vel = pygame.math.Vector2(0, 0)
SPEED = 30
movetimer = 0
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    
    apple_vel.x = 0
    apple_vel.y = 0
    snake_tracking = apple_pos - snake_pos
    if snake_tracking.length() > 0:
        snake_vel = snake_tracking.normalize() * SPEED
    else:
        snake_vel = pygame.math.Vector2(0, 0)
    distance = apple_pos.distance_to(snake_pos)
    if distance < 30:
        game_over = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:    apple_vel.y = -SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:  apple_vel.y = SPEED
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:  apple_vel.x = -SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: apple_vel.x = SPEED
    
    movetimer += 1
    if movetimer >= 60:
        apple_pos += apple_vel
        snake_pos += snake_vel
        movetimer = 0

    if game_over:
        screen.fill((255, 0, 0))
    else:
        screen.fill((30, 30, 30))  # Wipe background clean
        
        pygame.draw.circle(screen, (255, 50, 50), apple_pos, 20)
        pygame.draw.circle(screen, (0, 255, 0), snake_pos, 10)

    pygame.display.flip()
    clock.tick(200) 