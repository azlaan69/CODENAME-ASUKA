from os import kill
import pygame
import sys
import random
import time

class Player(pygame.sprite.Sprite):
	def __init__(self, x=10, y=10):
		super().__init__()
		self.image = pygame.Surface((1, 1))
		self.image.fill((255, 0, 0))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y) 
		self.hp = 1000
		self.iframe = -15
		self.charge = 0
	def update(self, tick, targetX, targetY, hazards):
		keys = pygame.key.get_pressed()
		tickcheck = False
		if tick % 5 == 0:
			tickcheck = True

		if keys[pygame.K_w] and tickcheck and self.rect.y > 1: self.rect.y -= 1
		if keys[pygame.K_s] and tickcheck and self.rect.y < 18: self.rect.y += 1
		if keys[pygame.K_a] and tickcheck and self.rect.x > 1: self.rect.x -= 1
		if keys[pygame.K_d] and tickcheck and self.rect.x < 18: self.rect.x += 1
		if keys[pygame.K_t]: self.rect.x, self.rect.y = 18, 18 #1-1 is top left inside borders, 18-18 is bottom right inside borders

class Snake(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.Surface((1, 1))
		self.image.fill((0, 255, 0))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.charging = False 
		self.dx = 0
		self.dy = 0

	def update(self, tick, targetX, targetY, hazards):

		if tick % 4 == 0:
			if not self.charging:			
				if self.rect.x < targetX: self.dx = 1
				elif self.rect.x > targetX: self.dx = -1 
				else: self.dx = 0

				if self.rect.y < targetY: self.dy = 1
				elif self.rect.y > targetY: self.dy = -1
				else: self.dy = 0
				
				if self.rect.x == targetX or self.rect.y == targetY:
					self.charging = True
					self.image.fill((255, 255, 0))
				else:
					pass
			self.rect.x += self.dx
			self.rect.y += self.dy

class Beam(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.Surface((1, 1))
		self.image.fill((165, 165, 165))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.timer = 0
	def update(self, tick, targetX, targetY, hazards):
		self.timer += 1
		if self.timer < 10:
			if self.timer % 2.5 == 0:
				self.image.fill((165, 165, 165))
			else:
				self.image.fill((100, 100, 100))
		elif self.timer == 10:
			self.image.fill((255, 255, 0))
			hazards.add(self)
		elif self.timer >= 15:
			hazards.remove(self)
			self.kill()

class Meteor(pygame.sprite.Sprite):
	def __init__(self, x, y, orientation):
		super().__init__()
		self.orientation = orientation

		if self.orientation == "V":
			self.image = pygame.Surface((4, 18))
			self.rect = self.image.get_rect()
			self.rect.topleft = (x, 1)
		else:
			self.image = pygame.Surface((18, 4))
			self.rect = self.image.get_rect()
			self.rect.topleft = (1, y)

		self.image.fill((100, 100, 100))
		self.timer = 0
	def update(self, tick, targetX, targetY, hazards):
		self.timer += 1
		
		if self.timer < 30:
			if self.timer % 6 < 2:
				self.image.fill((255, 255, 255))
			else:
				self.image.fill((100, 100, 100))

		elif 30 <= self.timer < 45:
			if self.timer % 3 == 0:
				self.image.fill((255, 0, 255))
			else:
				self.image.fill((0, 0, 255))
			hazards.add(self)

		elif self.timer >= 45:
			hazards.remove(self)
			self.kill()

pygame.init()
display = pygame.display.set_mode((400, 400))
playfield = pygame.Surface((20, 20))
tick = 0
clock = pygame.time.Clock()
killedsnakes = 25
font = pygame.font.Font(None, 50)

possiblepos = [
    (2, 2),   (10, 2),   (17, 2),   
    (2, 10),             (17, 10),  
    (2, 17),  (10, 17),  (17, 17)   
] 

hazards = pygame.sprite.Group()
meteors = pygame.sprite.Group()
beams = pygame.sprite.Group()
snakes = pygame.sprite.Group()
sprites = pygame.sprite.Group()
player = Player(10, 10)
sprites.add(player)

def Spawn():
    spawnX, spawnY = random.choice(possiblepos)
    snake = Snake(spawnX, spawnY)
    sprites.add(snake)
    snakes.add(snake)
def Spawn_Beam():
	if random.choice([True, False]):
		for posX in range(1, 19):
			beam = Beam(posX, player.rect.y)
			sprites.add(beam)
			beams.add(beam)
	else:
		for posY in range(1, 19):
			beam = Beam(player.rect.x, posY)
			sprites.add(beam)
			beams.add(beam)
def Spawn_Meteor():
	lanes = [1, 8, 15]
	orientation = random.choice(["H", "V"])
	chosenlane = random.choice(lanes)
	if orientation == "V":
		meteor = Meteor(chosenlane, 1, "V")
	else:
		meteor = Meteor(1, chosenlane, "H")
	meteors.add(meteor)
Spawn()

while True:
#here we check if game is running
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
#here we update
	tick += 1
	if tick % 30 == 0: 
		Spawn()

	if killedsnakes >= 10 and tick % 60 == 0: 
		Spawn_Beam()

	if killedsnakes >= 25 and tick % 120 == 0:
		Spawn_Meteor()

	sprites.update(tick, player.rect.x, player.rect.y, hazards)
	meteors.update(tick, player.rect.x, player.rect.y, hazards)
#here we collide
	for i in snakes:
		if i.rect.x > 18 or i.rect.x < 1 or i.rect.y > 18 or i.rect.y < 1:
			i.kill()
			killedsnakes += 1
			player.charge += 1
		if player.charge >= 5:
			player.charge = 0
			if player.hp < 3:
				player.hp += 1

	collcheck = pygame.sprite.spritecollide(player, snakes, False)
	if len(collcheck) > 0 and (tick - player.iframe) > 15:
		player.hp -= 1
		player.iframe = tick

	beamcollcheck = pygame.sprite.spritecollide(player, beams, False)
	if len(beamcollcheck) > 0 and (tick - player.iframe) > 15:
		for b in beamcollcheck:
			if b.timer >= 10:
				player.hp -= 1
				player.iframe = tick
				break

	meteorcollcheck = pygame.sprite.spritecollide(player, meteors, False)
	if len(meteorcollcheck) > 0 and (tick - player.iframe) > 15:
		for m in meteorcollcheck:
			if m.timer >= 30:
				player.hp -= 2
				player.iframe = tick
				break

	snakecollcheck = pygame.sprite.groupcollide(snakes, hazards, True, False)
	if len(snakecollcheck) > 0:
		for s in snakecollcheck:
			s.kill()
			player.charge += 1
			killedsnakes += 1

#here we draw
	playfield.fill((0, 0, 0))
	pygame.draw.rect(playfield, (255, 255, 255), (0, 0, 20, 20), 1)
	meteors.draw(playfield)
	sprites.draw(playfield)
	pygame.display.set_caption(f"HP: {player.hp} | Kills: {killedsnakes}")

#here we sync frames and output and also check death
	if player.hp <= 0:
		pygame.display.set_caption(f"Game Over! | Kills: {killedsnakes}")
		for i in sprites.sprites():
			i.kill()
		for j in meteors.sprites():
			j.kill()
		display.fill((0, 0, 0))
		overscreen = font.render("GAME OVER!", True, (255, 0, 0))
		display.blit(overscreen, (100, 200))
		pygame.display.flip()
		time.sleep(2)
		pygame.quit()
		sys.exit()

	else:
		frame = pygame.transform.scale(playfield, (400, 400))
		display.blit(frame)
		pygame.display.flip()
	print(tick)
	clock.tick(30)