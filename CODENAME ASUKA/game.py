import pygame
import sys
import math
import time
import random

pygame.init()
pygame.joystick.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

font = pygame.font.Font(None, 36)
bigfont = pygame.font.Font(None, 300)
sfx = {
    "parry": pygame.mixer.Sound("powerUp.wav"),
    "swing": pygame.mixer.Sound("pickupCoin.wav"),
    "hit": pygame.mixer.Sound("hitHurt.wav"),
    "beam": pygame.mixer.Sound("explosion.wav"),
    "failedparry": pygame.mixer.Sound("explosion (1).wav")
}

for sound in sfx.values():
    sound.set_volume(0.2)

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
controller = joysticks[0] if joysticks else None

window_width, window_height = 1400, 800
screen = pygame.display.set_mode((window_width, window_height))

playfield_size = 704
playfield = pygame.Surface((playfield_size, playfield_size))

playfield_x = (window_width - playfield_size) // 2
playfield_y = (window_height - playfield_size) // 2

clock = pygame.time.Clock()

clonespawncount = 0
drones = pygame.sprite.Group()
clones = pygame.sprite.Group()
beams = pygame.sprite.Group()
bullets = pygame.sprite.Group()
sprites = pygame.sprite.Group()

def load_spritesheet(filename, frame_w, frame_h, num_frames, scale_factor=8):
    spritesheet = pygame.image.load(filename).convert_alpha()
    frames = []
    for i in range(num_frames):
        startX = i * frame_w
        frame_rect = pygame.Rect(startX, 0, frame_w, frame_h)
        rawframe = spritesheet.subsurface(frame_rect)
        scaledframe = pygame.transform.scale_by(rawframe, scale_factor)
        frames.append(scaledframe)
    return frames

beamframes = load_spritesheet("beam-Sheet.png", 8, 8, 3)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = load_spritesheet("player-Sheet.png", 8, 8, 2)
        self.currentframe = 0
        self.animtimer = 0
        self.animspeed = 0.05

        self.hurtboxsurf = pygame.Surface((64, 64), pygame.SRCALPHA)
        pygame.draw.rect(self.hurtboxsurf, (255, 255, 255), (26, 30, 12, 12))

        self.image = self.frames[self.currentframe]
        self.rect = self.image.get_rect()
        self.rect.center = (320 , 600)
        self.x, self.y = 320, 576
        self.mask = pygame.mask.from_surface(self.hurtboxsurf)
        self.hp = 10
        self.iframes = 0

    def update(self, controller, tick):

        if self.iframes > 0:
            self.iframes -= 1

        self.animtimer += self.animspeed
        if self.animtimer > 1.0:
            self.animtimer = 0
            self.currentframe = (self.currentframe + 1) % len(self.frames)
            self.image = self.frames[self.currentframe]

        if controller:
            stick_x = controller.get_axis(0)
            stick_y = controller.get_axis(1)
            deadzone = 0.1
            speed = 8

            if abs(stick_x) > deadzone:
                self.x += stick_x * speed
            if abs(stick_y) > deadzone:
                self.y += stick_y * speed

            if self.x < 4: self.x = 4
            elif self.x > 640: self.x = 640
            
            if self.y < 256: self.y = 256
            elif self.y > 640: self.y = 640

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.mask = pygame.mask.from_surface(self.hurtboxsurf)

class Sword(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.rawimage = pygame.image.load("sword.png").convert_alpha()
        self.scaledimage = pygame.transform.scale(self.rawimage, (64, 64))
        self.source = self.scaledimage
        self.cd_img = self.scaledimage.copy()
        self.cd_img.fill((255, 0 , 0), special_flags=pygame.BLEND_RGB_MULT)
        self.image = self.source
        self.rect = self.image.get_rect()
        self.rawmask = pygame.mask.from_surface(self.image)

        self.hitboxsurf = pygame.Surface((5, 5))
        self.hitboxsurf.fill((255, 255, 255))
        self.hitbox = pygame.mask.from_surface(self.hitboxsurf)

        self.mask = self.rawmask.convolve(self.hitbox)

        self.angle = -15
        self.distance = 40

        self.parry_cooldown = 0
        self.isparrying = False
        self.parrywindow = 30
        self.justparried = False

    def update(self, controller, tick):
        if self.parry_cooldown > 0: self.parry_cooldown -= 1
        if controller:

            if controller.get_button(0) and self.parry_cooldown == 0 and self.isparrying == False:
                self.isparrying = True
                self.parrystart = time.time()
                sfx["swing"].play()

        if self.parry_cooldown > 0:
            self.source = self.cd_img
        else:
            self.source = self.scaledimage

        self.image = pygame.transform.rotate(self.source, self.angle)
        self.rect = self.image.get_rect()
        rad = math.radians(-self.angle)
        offset_x = math.cos(rad) * self.distance
        offset_y = math.sin(rad) * self.distance

        if self.isparrying == True:
            elapsed = time.time() - self.parrystart
            if elapsed < 0.1:
                self.angle += 36
                self.rawmask = pygame.mask.from_surface(self.image)
                self.mask = self.rawmask.convolve(self.hitbox)
            elif elapsed < 0.15:
                pass
                
            else:
                if self.angle > -15:
                    self.angle -= 60
                    self.rawmask = pygame.mask.from_surface(self.image)
                    self.mask = self.rawmask.convolve(self.hitbox)
                    if self.angle < -15: 
                        self.angle = -15
                        self.rawmask = pygame.mask.from_surface(self.image)
                        self.mask = self.rawmask.convolve(self.hitbox)
                else:
                    self.isparrying = False
                    if self.justparried:
                        self.parry_cooldown = 0
                        self.justparried = False
                    else:
                        self.parry_cooldown = 20
                self.rawmask = pygame.mask.from_surface(self.image)
                self.hitbox = pygame.mask.from_surface(self.hitboxsurf)
                self.rect.center = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
        self.rawmask = pygame.mask.from_surface(self.image)
        self.hitbox = pygame.mask.from_surface(self.hitboxsurf)
        self.rect.center = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)

class MarkerDrone(pygame.sprite.Sprite):
    def __init__(self, startx, endx, permtrack=False, speed=8):
        super().__init__()
        self.startpos = pygame.math.Vector2(startx, 230)
        self.endpos = pygame.math.Vector2(endx, 230)
        self.reached = False
        self.speed = speed

        self.rawimage = pygame.image.load("drone.png").convert_alpha()
        self.image = pygame.transform.scale_by(self.rawimage, 8)
        self.rect = self.image.get_rect()
        self.rect.center = self.startpos

        self.permtrack = permtrack

    def update(self, controller, tick):

        if self.permtrack:
            self.endpos = pygame.math.Vector2(player.rect.centerx, 230)
            self.reached = False

        if not self.reached:
            dir = self.endpos - self.startpos
            distance = dir.length()

            if distance > self.speed:
                dir = dir.normalize()
                self.startpos += dir * self.speed
            else:
                self.startpos = pygame.math.Vector2(self.endpos)
                self.reached = True

            self.rect.center = self.startpos

        if self.rect.right > 704: self.rect.right = 704
        if self.rect.left < 1: self.rect.left = 1


    def shift(self, new_endx):
        self.endpos = pygame.math.Vector2(new_endx, 230)
        self.reached = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velX, velY, bounceCount):
        super().__init__()
        self.parried = False
        self.rawimage = pygame.image.load("bullet.png").convert_alpha()
        self.scaledimage = pygame.transform.scale(self.rawimage, ((64, 64)))
        self.image = self.scaledimage
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.posX = float(self.rect.centerx)
        self.posY = float(self.rect.centery)
        self.velX = velX
        self.velY = velY
        self.mask = pygame.mask.from_surface(self.image)
        self.bounce = bounceCount

    def update(self, controller, tick):

        self.angle = math.degrees(math.atan2(-self.velY, self.velX)) - 90
        self.image = pygame.transform.rotate(self.scaledimage, self.angle)
        self.posX += self.velX
        self.posY += self.velY
        self.rect.centery = int(self.posY)
        self.rect.centerx = int(self.posX)
        self.mask = pygame.mask.from_surface(self.image)
        if self.bounce <= 0:
            if self.rect.right <= 0 or self.rect.left > 704 or self.rect.top < 256 or self.rect.bottom > 704:
                    self.kill()
        else:
            if self.rect.right <= 0 or self.rect.left > 704:
                self.angle += 90
                self.velX *= -1
                self.bounce -= 1
                self.mask = pygame.mask.from_surface(self.image)
                self.parried = False
            if self.rect.top < 256 or self.rect.bottom > 704:
                self.angle -= 90
                self.velY *= -1
                self.bounce -= 1
                self.mask = pygame.mask.from_surface(self.image)
                self.parried = False

class Beam(pygame.sprite.Sprite):
    def __init__(self, x, y, delay, starttick, beamframes):
        super().__init__()
        self.active = False

        self.frames = beamframes
        self.currentframe = 0
        self.animtimer = 0
        self.animspeed = 0.2

        self.image = self.frames[self.currentframe]

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.delay = delay
        self.alpha = 50
        self.image.set_alpha(self.alpha)
        self.lifetime = 0
        self.starttick = starttick

    def update(self, controller, tick):
        self.animtimer += self.animspeed
        if self.animtimer >= 1.0:
            self.currentframe = (self.currentframe + 1) % len(self.frames)
            self.image = self.frames[self.currentframe]
            self.animtimer = 0

        ticks_elapsed = tick - self.starttick
        if ticks_elapsed >= self.delay and self.alpha <= 255 and self.lifetime == 0:
            self.alpha += 15

        if self.alpha >= 255 and self.lifetime < 20:
            self.active = True
            self.lifetime += 1

        if self.lifetime >= 20:
            self.active = False
            self.alpha -= 10

        if self.alpha <= 0:
            self.kill()

        self.image.set_alpha(self.alpha)
        self.mask = pygame.mask.from_surface(self.image)

class Clone(pygame.sprite.Sprite):
    def __init__(self, x, y, left, player):
        super().__init__()
        self.player = player
        self.parried = False
        self.left = left

        self.frames = load_spritesheet("clone.png", 8, 8, 2)
        self.currentframe = 0
        self.animtimer = 0
        self.animspeed = 0.2

        self.x = x
        self.y = y

        self.image = self.frames[self.currentframe]
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.mask = pygame.mask.from_surface(self.image)

        self.counter = 1
        self.firstdest = (player.rect.centerx - 160 if not self.left else player.rect.centerx + 228, player.rect.centery + 16)
        self.seconddest = None
        self.thirddest = None
        self.hangtime = 0

    def update(self, controller, tick):

        self.seconddest = (self.player.rect.centerx + 128 if not self.left else self.player.rect.centerx - 128, self.player.rect.centery - 128)

        self.animtimer += self.animspeed
        if self.animtimer >= 1.0:
            self.currentframe = (self.currentframe + 1) % len(self.frames)
            self.image = self.frames[self.currentframe]
            self.animtimer = 0

        if self.hangtime > 0:
            self.hangtime -= 1
            if self.hangtime == 0:
                self.parried = False
                self.rect.center = (self.x, self.y)

        if self.counter == 1:
            targetpos = pygame.math.Vector2(self.firstdest)
            currentpos = pygame.math.Vector2(self.x, self.y)

        elif self.counter == 2:
            targetpos = pygame.math.Vector2(self.seconddest)
            currentpos = pygame.math.Vector2(self.x, self.y)

        elif self.counter == 3:
            targetpos = pygame.math.Vector2(self.thirddest)
            currentpos = pygame.math.Vector2(self.x, self.y)

        elif self.counter == 4:
            targetpos = pygame.math.Vector2(self.player.rect.center)
            currentpos = pygame.math.Vector2(self.x, self.y)

        elif self.counter > 4:
            targetpos = None
            currentpos = None
            self.kill()
            return

        collcheck = self.x < 1 or self.x > 704 or self.y < 256 or self.y > 704 

        if self.counter < 5:
            dir = targetpos - currentpos
            distance = dir.length()
            speed = 16

            if distance > speed and self.hangtime == 0:
                dir = dir.normalize()
                currentpos += dir * speed
                self.x, self.y = currentpos.x, currentpos.y

            elif distance < speed or collcheck:
                self.counter += 1
                self.hangtime = 5
                self.thirddest = (self.rect.centerx - 240 if not self.left else self.rect.centerx + 256, self.rect.centery)


            elif self.parried:
                self.parried = False
                self.counter += 1
                self.hangtime = 5
                self.thirddest = (self.rect.centerx - 240 if not self.left else self.rect.centerx + 256, self.rect.centery)


        self.rect.center = (self.x, self.y)
        self.mask = pygame.mask.from_surface(self.image)

def Spawn_Bullet(SpawnCount, x, y, velX, velY, bounceCount):
    for i in range(SpawnCount):
        bullet = Bullet(x, y, velX, velY, bounceCount)
        bullets.add(bullet)
        sprites.add(bullet)

def Spawn_TrackBullet(spawnX, spawnY, vel, bounceCount):
    dx = player.rect.centerx - spawnX
    dy = player.rect.centery - spawnY

    angle = math.atan2(dx, dy)

    velX = math.sin(angle) * vel
    velY = math.cos(angle) * vel

    bullet = Bullet(spawnX, spawnY, velX, velY, bounceCount)
    bullets.add(bullet)
    sprites.add(bullet)

    bullet.update(controller, tick)


def Spawn_Beam(x, starttime):
    elapsed = time.time() - starttime
    for i in range(7):
        beam = Beam(x, 292 + (i * 64), i * 4, tick, beamframes)
        sprites.add(beam)
        beams.add(beam)
        sfx["beam"].play()

def Spawn_Clone():
    global clonespawncount
    if clonespawncount % 2 == 0:
        clone = Clone(640, 192, False, player)
    else:
        clone = Clone(64, 192, True, player)
    clonespawncount += 1
    sprites.add(clone)
    clones.add(clone)

def Spawn_Drones(end1, end2=False, permtrack=False, group=None, speed=8): #64, 640 are the edges
    if not end2:
        drone1 = MarkerDrone(352, end1, permtrack, speed)
        drones.add(drone1)
        sprites.add(drone1)
    else:
        drone1 = MarkerDrone(352, end1, permtrack, speed)
        drones.add(drone1)
        sprites.add(drone1)

        drone2 = MarkerDrone(352, end2, permtrack, speed)
        drones.add(drone2)
        sprites.add(drone2)

    if group is not None:
        group.add(drone1)
        if end2: group.add(drone2)

class Boss(pygame.sprite.Sprite):
    def __init__(self, x=64, y=16):
        super().__init__()
        self.frameW = 72
        self.frameH = 24

        self.frames = load_spritesheet("valkyrie-Sheet.png", 72, 24, 4)
        self.currentframe = 0

        self.image = self.frames[self.currentframe]
        self.rect = self.image.get_rect()
        self.rect.midtop = (704 // 2, 24)
        self.animtimer = 0
        self.animspeed = 0.1

        self.combos = [""]
        self.patterns = {
        "AreaDenial" : 0,
        "ParryCheck" : 0,
        "CloneHell" : 0
        }

        self.currentpattern = "IDLE"
        self.cooldown = 60
        self.attackstage = 1
        self.stagetimer = 0

        self.sidedrones = pygame.sprite.Group()
        self.maindrones = pygame.sprite.Group()
        self.isfiring = False

    def update(self, controller, tick):

        self.animtimer += self.animspeed
        if self.animtimer >= 1.0:
            self.currentframe = (self.currentframe + 1) % len(self.frames)
            self.image = self.frames[self.currentframe]
            self.animtimer = 0

        if self.currentpattern == "IDLE":
            if self.cooldown > 0:
                self.cooldown -= 1
            else:
                self.availablepatterns = ["AreaDenial", "CloneHell", "ParryCheck"] # AreaDenial, ParryCheck, CloneHell

                bias = {p: self.patterns[p] for p in self.availablepatterns}
                bias["CloneHell"] -= 2
                minuse = min(self.patterns[p] for p in self.availablepatterns)
                leastused = [p for p in self.availablepatterns if self.patterns[p] == minuse]

                self.currentpattern = random.choice(leastused)
                self.patterns[self.currentpattern] += 1
                self.patterntimer = 0

        if self.currentpattern != "IDLE":

            if self.currentpattern == "AreaDenial":

                if self.attackstage == 1: # amuse-bouche
                    self.maindrones.empty()
                    self.sidedrones.empty()    
                    for d in drones: d.kill()

                    Spawn_Drones(192, 512, group = self.maindrones, permtrack = False, speed = 8)
                    self.attackstage = 2
                    self.stagetimer = 60

                def soup1():
                    for d in self.maindrones:
                        Spawn_Beam(d.rect.centerx, time.time())
                    Spawn_Drones(64, 640, group = self.sidedrones, permtrack = False, speed = 8) 

                def soup2():
                    for d in self.sidedrones:
                        Spawn_Beam(d.rect.centerx, time.time())


                def soup():
                    for d in drones:
                        Spawn_Beam(d.rect.centerx, time.time())

                def shift():
                    for num, d in enumerate(drones):
                        shiftval = None
                        if num == 0: shiftval = 320-32
                        if num == 1: shiftval = 384+32 
                        if num == 2: shiftval = 192-32
                        if num == 3: shiftval = 512+32

                        d.shift(shiftval) 

                def appetizer():
                    Spawn_Bullet(1, 64, 64+256, 16, 16, 4)
                    Spawn_Bullet(1, 64, 640, 16, -16, 4)
                    Spawn_Bullet(1, 640, 64+256, -16, 16, 4)
                    Spawn_Bullet(1, 640, 640, -16, -16, 4) 

                    Spawn_Bullet(1, 1, 480, 24, 0, 4)
                    Spawn_Bullet(1, 703, 480, -24, 0, 4)
                    Spawn_Bullet(1, 352, 290, 0, 24, 4)
                    Spawn_Bullet(1, 352, 670, -0, -24, 4)
                 
                self.exec(2, 45, soup1)
                self.exec(3, 45, soup2)
                self.exec(4, 60, appetizer)
                self.exec(5, 45, soup)
                self.exec(6, 45, shift)
                self.exec(7, 45, soup)
                self.exec(8, 45, appetizer)
                self.exec(9, 120, "kill")

            if self.currentpattern == "ParryCheck":

                if self.isfiring == True:
                        if tick % 12 == 0:
                            for d in drones:
                                Spawn_Bullet(1, d.rect.centerx, 290, 0, 16, 0)

                def appetizer():

                    if len(drones) > 1: d.kill()
                    elif len(drones) < 1: Spawn_Drones(player.rect.x+32, permtrack=True)
                    Spawn_Clone()

                def seafood():
                    xpos = 1
                    for i in range(11):
                        Spawn_Bullet(1, xpos, 290, 0, 16, 0)
                        xpos += 64

                def intermizzo():
                    for d in drones:
                        Spawn_Beam(d.rect.centerx, time.time())

                if 2 <= self.attackstage <= 3: # soup
                    self.isfiring = True
                else:
                    self.isfiring = False

                self.exec(1, 30, appetizer)
                self.exec(2, 30, "pause")
                self.exec(3, 30, appetizer )
                self.exec(4, 30, seafood)
                self.exec(5, 60, intermizzo)
                self.exec(6, 60, intermizzo)
                self.exec(7, 30, appetizer)
                self.exec(8, 30, appetizer)
                self.exec(9, 60, "kill", False)

            if self.currentpattern == "CloneHell":

                if self.isfiring == True:
                    if tick % 12 == 0:
                        Spawn_TrackBullet(640, 290, 16, 0)
                    elif tick % 6 == 0:
                        Spawn_TrackBullet(64, 290, 16, 0)
                        

                self.isfiring = True if 3 >= self.attackstage > 2 else False

                self.exec(1, 90, lambda: [Spawn_Clone(), Spawn_Clone()])
                self.exec(2, 30, "pause")
                self.exec(3, 30, "beam")
                self.exec(4, 30, lambda: [Spawn_Clone(), Spawn_Clone()])
                self.exec(5, 30, "kill")




    def exec(self, neededstage, cooldown, actionfunc, killperm=True):
        if self.attackstage == neededstage:
            if self.stagetimer > 0:
                self.stagetimer -= 1
            else:
                if actionfunc == "kill":
                    if killperm:
                        for d in drones: d.kill()
                    self.currentpattern = "IDLE"
                    self.attackstage = 1
                elif actionfunc == "pause":
                    self.attackstage += 1
                    self.stagetimer = cooldown
                elif actionfunc == "beam":
                    Spawn_Beam(player.rect.centerx, time.time())
                    self.attackstage += 1
                    self.stagetimer = cooldown             
                else:
                    actionfunc()
                    self.attackstage += 1
                    self.stagetimer = cooldown

class Style:
    def __init__(self):
        self.rank = "D"
        self.points = 0
        self.decay = 0
        self.remmultiplier = 0.5
        self.thresholds = {
        "D": 0,
        "C": 1200,
        "B": 2500,
        "A": 5000,
        "S": 15000
        }
    def add(self, amount):
        self.points += amount
        self.decay = 0
    def rem(self, amount=1.0):
        penalty = self.remmultiplier * amount
        self.points *= (1.0 - penalty)
    def update(self, boss, player, sword):
        if self.points > 0 and boss.currentpattern != "IDLE": self.decay += 1
        if self.decay >= 180: self.points -= 5

        for rank, threshold in self.thresholds.items():
            if self.points > threshold:
                self.rank = rank

        if self.points > 5000:
            if tick % 200 == 0 and player.hp < 10: player.hp += 1
            sword.parry_cooldown = 0
            self.remmultiplier = 0.25

player = Player()
sword = Sword(player)
style = Style()

valkyrie = Boss(x=352, y=16)

sprites.add(sword)
sprites.add(player)
sprites.add(valkyrie)
tick = 0

messages = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

# DEBUG SPAWNS
    # if tick % 200 == 0:
    #     bullet = Bullet(player.rect.centerx, 300, 0, 16, 0)
    #     bullets.add(bullet)
    #     sprites.add(bullet)

    # if tick % 200 == 0:
    #     Spawn_Beam(player.rect.centerx, time.time())

    # if tick % 100 == 0 and len(clones) < 1:
    #     Spawn_Clone()

    # if tick % 100 == 0 and len(clones) < 1:
    #     Spawn_Drones()

    sprites.update(controller, tick)
    style.update(valkyrie, player, sword)

    messages[:] = [m for m in messages if tick < m[1]]

#  COLLISIONS
    for b in bullets:
        if pygame.sprite.collide_mask(sword, b):
            if sword.isparrying and not b.parried:
                sfx["swing"].stop()
                sfx["parry"].play()
                b.velY *= -1
                b.velX *= -1
                b.parried = True

                sword.angle = -15
                sword.isparrying = False
                sword.parry_cooldown = 0
                sword.parrystart = 0
                sword.justparried = True
                style.add(150)

                player.iframes += 15
                messages.append(("PERFECT PARRY!", tick + 60, (255, 255, 0)))
                continue

        if pygame.sprite.collide_mask(player, b) and player.iframes <= 0:
            if b.parried:
                continue

            sfx["hit"].play()
            messages.append(("DAMAGE TAKEN!", tick + 60, (255, 0, 0)))
            style.rem(1.6)
            player.iframes = 30
            player.hp -= 1

    for b in beams:
        if pygame.sprite.collide_mask(sword, b):
            if sword.isparrying and b.active:
                if not style.points > 15000:
                    sfx["swing"].stop()
                    sfx["failedparry"].play()
                    style.add(75)
                    messages.append(("PARRY OVERLOADED!", tick + 60, (200, 0, 0 ))) 
                    player.hp -= 1
                    player.iframes += 15

                else:
                    sfx["swing"].stop()
                    sfx["parry"].play()
                    style.add(250)
                    messages.append(("DARING PARRY!", tick + 60, (255, 0, 255)))
                    player.hp += 1
                    player.iframes += 30
                    b.active = False

                sword.angle = -15
                sword.isparrying = False
                sword.parry_cooldown = 120
                sword.parrystart = 0
                sword.justparried = True

                continue

        if pygame.sprite.collide_mask(player, b) and player.iframes <= 0 and b.active and not sword.justparried:

            sfx["hit"].play()
            messages.append(("DAMAGE TAKEN!", tick + 60, (255, 0, 0)))
            style.rem()
            player.iframes = 30
            player.hp -= 3

    for b in clones:
        if pygame.sprite.collide_mask(sword, b):
            if sword.isparrying and not b.parried:
                sfx["swing"].stop()
                sfx["parry"].play()
                b.parried = True

                sword.angle = -15
                sword.isparrying = False
                sword.parry_cooldown = 0
                sword.parrystart = 0
                sword.justparried = True
                style.add(250)

                player.iframes += 15
                messages.append(("PERFECT PARRY!", tick + 60, (255, 255, 0)))
                continue

        if pygame.sprite.collide_mask(player, b) and player.iframes <= 0:
            if b.parried:
                continue

            sfx["hit"].play()
            messages.append(("DAMAGE TAKEN!", tick + 60, (255, 0, 0)))
            style.rem()
            player.iframes = 30
            player.hp -= 1

    screen.fill((0, 0, 0))

    boss = font.render("TECHNO-VALKYRIE ASUKA, THE LAST TYRANT", True, (255, 50, 50))
    screen.blit(boss, (window_width // 2 - boss.get_width() // 2, 10))

    hud = font.render(f"HP: {player.hp}/10", True, (255, 255, 255))
    screen.blit(hud, (window_width // 2 - hud.get_width() // 2, playfield_y + playfield_size + 15))

    start_y = 400
    for idx, (text_str, decay, color) in enumerate(messages):
        message = font.render(text_str, True, color)
        screen.blit(message, (1100, start_y + (idx * 40)))

    stylecount = font.render(f"STYLE: {int(style.points)}", True, (255, 255, 255))
    stylerank = bigfont.render(style.rank, True, (255, 0, 0))

    screen.blit(stylecount, (1100, 300))
    screen.blit(stylerank, (1100, 100))

    playfield.fill((0, 0, 0)) 
    for x in range(0, 704, 64):
        for y in range(256, 704, 64):
            pygame.draw.rect(playfield, (0, 100, 0), (x, y, 64, 64), 1)
    
    sprites.draw(playfield)
    pygame.draw.rect(playfield, (0, 255, 0), (0, 256, 704, 448), 4)
    screen.blit(playfield, (playfield_x, playfield_y))
    
    pygame.display.flip()
    tick += 1
    clock.tick(60)