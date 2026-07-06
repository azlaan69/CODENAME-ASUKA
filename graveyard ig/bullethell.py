import curses
import random
from time import sleep

class Player:
    def __init__(self, posX, posY):
        self.x = posX
        self.y = posY 
        self.icon = 'O'
    def move(self, input, boundX, boundY):
        x = 0
        y = 0
        
        if input == ord('w'):
            y = -1
        elif input == ord('s'):
            y = 1
            
        if input == ord('a'):
            x = -1
        elif input == ord('d'):
            x = 1
        
        if x != 0 and (0 < self.x + x < boundX):
            self.x += x
        if y != 0 and (0 < self.y + y < boundY):
            self.y += y
            
    def draw(self, grid):
        grid.addstr(self.y, self.x, self.icon)
        
class Projectile:
    def __init__(self):
        pass

def main(grid):
    curses.curs_set(0)
    grid.nodelay(True)
    
    boundX = 51
    boundY = 21
    
    player = Player(25, 10)
    
    while True:
        grid.clear()
        
        for g1 in range(boundY):
            for g2 in range(boundX):
                grid.addstr(g1, g2, "·")
        for xborder in range(boundX):
            grid.addstr(0, xborder, '═')
            grid.addstr(20, xborder, '═')
        for yborder in range(boundY):
            grid.addstr(yborder, 0, '║')
            grid.addstr(yborder, 50, '║')
        
        grid.addstr(0, 0, "╔")
        grid.addstr(0, 50, "╗")
        grid.addstr(20, 0, "╚")
        grid.addstr(20, 50, "╝")
        
        input = grid.getch()
        player.move(input, boundX, boundY)
        player.draw(grid)
        grid.refresh()
curses.wrapper(main)