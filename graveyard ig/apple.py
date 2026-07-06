import pygame
import random
import sys
#39-39 is bottom right, 1-1 is top left
class Apple(pygame.sprite.Sprite):
	def __init__(self):
		self.delaycounter = 0
		self.speed = 1
		self.hp = 3
		self.pos = pygame.math.Vector2(20, 20)
		self.vel = pygame.math.Vector2(0, 0)
	def controls(self, key):
		self.vel = pygame.math.Vector2(0, 0)
		self.delaycounter += 1
		if self.delaycounter >= 30:
			if key[pygame.K_w]: self.vel.y = -self.speed
			if key[pygame.K_s]: self.vel.y = self.speed
			if key[pygame.K_a]: self.vel.x = -self.speed
			if key[pygame.K_d]: self.vel.x = self.speed
			if key[pygame.K_t]: self.pos = pygame.math.Vector2(1, 1)
			self.delaycounter = 0
	def move(self):
		self.pos += self.vel
	def collisions(self):
		if self.pos.x > 39 or self.pos.x < 1 or self.pos.y > 39 or self.pos.y < 1:
			self.hp -= 1
			self.pos = pygame.math.Vector2(random.randint(5, 35), random.randint(5, 35))

class snakeMain:
	def __init__(self):
		self.speed = 1
		self.vel = pygame.math.Vector2(0, 0)
		self.pos = pygame.math.Vector2(random.randint(5, 35), random.randint(5, 35))
		self.delaycounter = 0
	def move(self, applepos):
			self.delaycounter += 1
			if self.delaycounter >= 45:
				self.tracking = applepos - self.pos
				if self.tracking.length() > 0:
					self.vel = self.tracking.normalize() * self.speed
					self.pos += self.vel
				else:
					self.vel = pygame.math.Vector2(0, 0)

				self.delaycounter = 0


pygame.init()
screen = pygame.display.set_mode((400, 400))
canvas = pygame.Surface((40, 40))
pygame.display.set_caption("CONTROLS: W/A/S/D")
clock = pygame.time.Clock()
apple = Apple()
snake = snakeMain()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
	keys = pygame.key.get_pressed()
	apple.controls(keys)
	apple.move()
	snake.move(apple.pos)
	apple.collisions()

	canvas.fill((10, 10, 10))
	appleSprite = pygame.Rect(int(apple.pos.x), int(apple.pos.y), 1, 1)
	snakeSprite = pygame.Rect(int(snake.pos.x), int(snake.pos.y), 1, 1)
	pygame.draw.rect(canvas, (255, 0, 0), appleSprite)
	pygame.draw.rect(canvas, (0, 255, 0), snakeSprite)
	pygame.draw.rect(canvas, (255, 255, 255), (0, 0, 40, 40), 1)

	scaled_frame = pygame.transform.scale(canvas, (400, 400))
	screen.blit(scaled_frame, (0, 0))
	pygame.display.flip()
	print(snake.vel)
	clock.tick(200)