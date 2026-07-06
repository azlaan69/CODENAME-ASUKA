from os import kill
import pygame
import sys
import random
import time

pygame.init()
tile = 40 
playfield = pygame.display.set_mode((800, 800))
tick = 0
clock = pygame.time.Clock()
killedsnakes = 25
font = pygame.font.Font(None, 50)

possiblepos = [
    (2 * tile, 2 * tile),  (10 * tile, 2 * tile),  (17 * tile, 2 * tile),   
    (2 * tile, 10 * tile),                         (17 * tile, 10 * tile),  
    (2 * tile, 17 * tile), (10 * tile, 17 * tile), (17 * tile, 17 * tile)   
] 

class Player(pygame.sprite.Sprite):
	def __init__(self, x=10*tile, y=10*tile):
		super().__init__()
		raw_image = pygame.image.load("apple.png").convert_alpha()
		self.image = pygame.transform.scale(raw_image, (tile, tile))
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

		if keys[pygame.K_w] and tickcheck and self.rect.y > 1 * tile: self.rect.y -= tile
		if keys[pygame.K_s] and tickcheck and self.rect.y < 18 * tile: self.rect.y += tile
		if keys[pygame.K_a] and tickcheck and self.rect.x > 1 * tile: self.rect.x -= tile
		if keys[pygame.K_d] and tickcheck and self.rect.x < 18 * tile: self.rect.x += tile
		if keys[pygame.K_t]: self.rect.x, self.rect.y = 18 * tile, 18 * tile

class Snake(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		raw_tracking = pygame.image.load("snake.png").convert_alpha()
		raw_charging = pygame.image.load("snake_inverted.png").convert_alpha()
		
		self.tracking_img = pygame.transform.scale(raw_tracking, (tile, tile))
		self.charging_img = pygame.transform.scale(raw_charging, (tile, tile))
		
		self.image = self.tracking_img
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.charging = False 
		self.dx = 0
		self.dy = 0

	def update(self, tick, targetX, targetY, hazards):
		if tick % 4 == 0:
			if not self.charging:			
				if self.rect.x < targetX: self.dx = tile
				elif self.rect.x > targetX: self.dx = -tile
				else: self.dx = 0

				if self.rect.y < targetY: self.dy = tile
				elif self.rect.y > targetY: self.dy = -tile
				else: self.dy = 0
				
				if self.rect.x == targetX or self.rect.y == targetY:
					self.charging = True
					self.image = self.charging_img
			
			self.rect.x += self.dx
			self.rect.y += self.dy

class Beam(pygame.sprite.Sprite):
	def __init__(self, x, y, orientation="H"):
		super().__init__()
		self.orientation = orientation
		
		raw_body = pygame.image.load("beamsnake-body.png").convert_alpha()
		
		if self.orientation == "V":
			self.activeimage = pygame.transform.scale(raw_body, (tile, 18 * tile))
			self.image = pygame.Surface((tile, 18 * tile))
			self.image.fill((165, 165, 165))
		else:
			self.activeimage = pygame.transform.scale(raw_body, (18 * tile, tile))
			self.image = pygame.Surface((18 * tile, tile))
			self.image.fill((165, 165, 165))
			
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.timer = 0

	def update(self, tick, targetX, targetY, hazards):
		self.timer += 1
		if self.timer < 10:
			if self.timer % 2 == 0:
				if self.orientation == "V":
					self.image = pygame.Surface((tile, 18 * tile))
				else:
					self.image = pygame.Surface((18 * tile, tile))
				self.image.fill((165, 165, 165))
			else:
				if self.orientation == "V":
					self.image = pygame.Surface((tile, 18 * tile))
				else:
					self.image = pygame.Surface((18 * tile, tile))
				self.image.fill((100, 100, 100))
		elif self.timer == 10:
			self.image = self.activeimage
			hazards.add(self)
		elif self.timer >= 15:
			hazards.remove(self)
			self.kill()

class Meteor(pygame.sprite.Sprite):
	def __init__(self, x, y, orientation):
		super().__init__()
		self.orientation = orientation

		if self.orientation == "V":
			self.image = pygame.Surface((4 * tile, 18 * tile))
			self.rect = self.image.get_rect()
			self.rect.topleft = (x, 1 * tile)
		else:
			self.image = pygame.Surface((18 * tile, 4 * tile))
			self.rect = self.image.get_rect()
			self.rect.topleft = (1 * tile, y)

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

hazards = pygame.sprite.Group()
meteors = pygame.sprite.Group()
beams = pygame.sprite.Group()
snakes = pygame.sprite.Group()
sprites = pygame.sprite.Group()

player = Player(10 * tile, 10 * tile)
sprites.add(player)

def Spawn():
	spawnX, spawnY = random.choice(possiblepos)
	snake = Snake(spawnX, spawnY)
	sprites.add(snake)
	snakes.add(snake)

def Spawn_Beam():
	if random.choice([True, False]):
		beam = Beam(1 * tile, player.rect.y, "H")
		sprites.add(beam)
		beams.add(beam)
	else:
		beam = Beam(player.rect.x, 1 * tile, "V")
		sprites.add(beam)
		beams.add(beam)

def Spawn_Meteor():
	lanes = [1 * tile, 8 * tile, 15 * tile]
	orientation = random.choice(["H", "V"])
	chosenlane = random.choice(lanes)
	if orientation == "V":
		meteor = Meteor(chosenlane, 1 * tile, "V")
	else:
		meteor = Meteor(1 * tile, chosenlane, "H")
	meteors.add(meteor)
	sprites.add(meteor)

Spawn()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	tick += 1
	if tick % 30 == 0: 
		Spawn()
	if killedsnakes >= 10 and tick % 60 == 0: 
		Spawn_Beam()
	if killedsnakes >= 25 and tick % 120 == 0:
		Spawn_Meteor()

	sprites.update(tick, player.rect.x, player.rect.y, hazards)
	meteors.update(tick, player.rect.x, player.rect.y, hazards)

	for i in snakes:
		if i.rect.x > 18 * tile or i.rect.x < 1 * tile or i.rect.y > 18 * tile or i.rect.y < 1 * tile:
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

	playfield.fill((0, 0, 0))
	
	pygame.draw.rect(playfield, (255, 255, 255), (0, 0, 20 * tile, 20 * tile), tile)
	
	sprites.draw(playfield)
	pygame.display.set_caption(f"HP: {player.hp} | Kills: {killedsnakes}")

	if player.hp <= 0:
		pygame.display.set_caption(f"Game Over! | Kills: {killedsnakes}")
		for i in sprites.sprites(): i.kill()
		for j in meteors.sprites(): j.kill()
		playfield.fill((0, 0, 0))
		overscreen = font.render("GAME OVER!", True, (255, 0, 0))
		playfield.blit(overscreen, (250, 380))
		pygame.display.flip()
		time.sleep(2)
		pygame.quit()
		sys.exit()
	else:
		pygame.display.flip()
		
	print(tick)
	clock.tick(30)