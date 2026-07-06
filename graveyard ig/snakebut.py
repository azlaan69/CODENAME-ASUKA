import curses
import time
import random

class Arena:
    def __init__(self, width=50, height=22):
        self.width = width
        self.height = height
    def draw(self, grid, apple):
        for i in range(0, self.height+1):
            for j in range(0, self.width+1):
                grid.addstr(i, j, "Â·")
        for x in range(0, self.width + 1):
            grid.addstr(0, x, 'â•')
            grid.addstr(self.height, x, 'â•')
        for y in range(0, self.height + 1):
            grid.addstr(y, 0, 'â•‘')
            grid.addstr(y, self.width, 'â•‘')
        grid.addstr(0, 0, "â•”")
        grid.addstr(0, self.width, "â•—")
        grid.addstr(self.height, 0, "â•š")
        grid.addstr(self.height, self.width, "â•")
        grid.addstr(26, 2, "Reach 10 Bites to Level Up!")
        if apple.bites < 10:
            grid.addstr(27, 2, f"Bites: {apple.bites}")
        elif apple.bites >= 10:
            grid.addstr(27, 2, f"Bites: {apple.bites - 10}")
        if apple.phase == 1.0:
            grid.addstr(24, 2, "Turn back. The apple is not for thee.")
        elif apple.phase == 2.0:
            grid.addstr(24, 2, "It is too late. Thou shalt know true fear now.")

class Snake:
    def __init__(self, sY = 11, sX = 25):
        self.Y = sY
        self.X = sX
        self.icon = 'H'
        self.dir = 'w'
        self.cooldown = 0.15
        self.move_anchor = time.time()
    def controls(self, key):
        if key in [119, 97, 115, 100]: #ordinal values, wasd
            self.dir = chr(key)
    def movement(self):
        if time.time() - self.move_anchor >= self.cooldown:
            if self.dir == 'w': self.Y -= 1
            if self.dir == 's': self.Y += 1
            if self.dir == 'a': self.X -= 1
            if self.dir == 'd': self.X += 1
            self.move_anchor = time.time()
    def draw(self, grid):
        grid.addstr(self.Y, self.X, self.icon)

class Apple():
    def __init__(self):
        self.Y = random.randint(1, 21)
        self.X = random.randint(1, 49)
        self.icon = 'O'
        self.bites = 0
        self.phase = 0.0
        self.hasran = False
        self.ticktimer = 0
        self.tick = 0
        self.clone = False
    def move(self):
        self.X = random.randint(1, 49)
        self.Y = random.randint(1, 21)
    def draw(self, grid, arena):
        grid.addstr(self.Y, self.X, self.icon)
        if self.clone:
            self.cY = arena.height - self.Y
            self.cX = arena.width - self.X
            grid.addstr(self.cY, self.cX, self.icon)
    def phasecheck(self, snake, grid):
        if self.bites == 5:
            self.phase = 0.5
            snake.cooldown = 0.135
        if self.bites == 10 and self.phase == 0.5:
            self.phase = 1.0
            snake.cooldown = 0.12
            self.ticktimer = time.time()
        elif self.bites == 15 and self.phase == 1.0:
            self.phase = 2.0
            snake.cooldown = 0.105
            self.ticktimer = time.time()
        elif self.bites == 20 and self.phase == 2.0:
            self.phase = 3.0
            snake.cooldown = 0.09
            self.ticktimer = time.time()
        if self.phase == 0.5:
            x = self.X - snake.X
            y = self.Y - snake.Y
            if abs(x) + abs(y) <= 5 and self.hasran == False:
                self.move()
                self.hasran = True
        if self.phase >= 1.0:
            self.phase1(grid, snake)
    def phase1(self, grid, snake):
        elapsedtime = time.time() - self.ticktimer
        if elapsedtime >= 0.5 and self.phase >= 1.0:
            self.tick += 1
            self.ticktimer = time.time()
        if self.phase == 1.0:
            if self.tick == 1 or self.tick == 3:
                for i in range(1, 50):
                    grid.addstr(self.Y, i, "-", curses.A_BOLD)
                    grid.addstr(self.Y-1, i, "-", curses.A_BOLD)
                    grid.addstr(self.Y+1, i, "-", curses.A_BOLD)
            if self.tick == 2 or self.tick == 4:
                for i in range(1, 22):
                    grid.addstr(i, self.X, "|", curses.A_BOLD)
                    grid.addstr(i, self.X-1, "|", curses.A_BOLD)
                    grid.addstr(i, self.X+1, "|", curses.A_BOLD)
            if self.tick >= 8:
                self.move()
                self.tick = 1

        elif self.phase == 2.0:
            self.clone = True
            if self.tick == 1:
                for i in range(1, 50):
                    grid.addstr(self.Y, i, "-", curses.A_BLINK)
                for j in range(1, 22):
                    grid.addstr(j, self.X, "|", curses.A_BLINK)
                for k in range(1, 50):
                    grid.addstr(self.cY, k, "-", curses.A_BLINK)
                for l in range(1, 22):
                    grid.addstr(l, self.cX, "|", curses.A_BLINK)
            if self.tick == 2:
                for i in range(1, 50):
                    grid.addstr(self.Y, i, "-", curses.A_BOLD)
                for j in range(1, 22):
                    grid.addstr(j, self.X, "|", curses.A_BOLD)
                for k in range(1, 50):
                    grid.addstr(self.cY, k, "-", curses.A_BOLD)
                for l in range(1, 22):
                    grid.addstr(l, self.cX, "|", curses.A_BOLD)
            if self.tick >= 5:
                self.move()
                self.tick = 1

        elif self.phase == 3.0:
            pass
                
def collision(snake, apple, arena):
    #normal
    if snake.Y == apple.Y and snake.X == apple.X:
        apple.move()
        apple.bites += 1
        apple.hasran = False
    #clone + wallphase
    if apple.phase >= 2.0:
        if snake.Y == apple.cY and snake.X == apple.cX:
            apple.move()
            apple.bites += 1
            apple.hasran = False
        if snake.Y <= 0: snake.Y = 21
        if snake.Y >= 22: snake.Y = 1
        if snake.X <= 0: snake.X = 49
        if snake.X >= 50: snake.X = 1
    #wall collisions
    if snake.Y <= 0 or snake.Y >= arena.height or snake.X <= 0 or snake.X >= arena.width:
        return True
    #beam
    if apple.phase == 1.0 and apple.phase < 2.0:
        if apple.Y == snake.Y and apple.tick == 1 or apple.Y == snake.Y and apple.tick == 3 or apple.X == snake.X and apple.tick == 2 or apple.X == snake.X and apple.tick == 4:
            return True
    #phase 2 telegraphed beam
    elif apple.phase == 2.0 and apple.tick == 2:
        if apple.Y == snake.Y or apple.cY == snake.Y or apple.X == snake.X or apple.cX == snake.X:
            return True

def main(grid):
    snake = Snake()
    apple = Apple()
    arena = Arena()
    curses.curs_set(0)
    grid.nodelay(True)
    grid.clear()
    arena.draw(grid, apple)
    grid.refresh()
    while True:
        key = grid.getch()
        if key == ord('i'): break
        if key == ord('t'): apple.bites += 5
        snake.controls(key)
        snake.movement()
        arena.draw(grid, apple)
        snake.draw(grid)
        apple.phasecheck(snake, grid)
        apple.draw(grid, arena)
        game_over = collision(snake, apple, arena)
        if game_over:
            grid.addstr(24, 22, "Game Over!", curses.A_BOLD)
            arena.draw(grid, apple)
            grid.refresh()
            time.sleep(3)
            break

        grid.refresh()
        time.sleep(0.0166)

curses.wrapper(main)