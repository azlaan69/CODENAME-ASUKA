import curses
import time
import random
def main(abc):
    curses.curs_set(0)
    abc.nodelay(True)
    y = 10
    x = 25
    speed = 0.5
    headdir = 'W'
    apx, apy = random.randint(5, 44), random.randint(5, 14)
    while True:
        abc.clear()
        for row in range(0, 21):
            for col in range(0, 51):
                abc.addstr(row, col, "·")
        for xborder in range(0, 51):
            abc.addstr(0, xborder, '═')
            abc.addstr(20, xborder, '═')
        for yborder in range(0, 21):
            abc.addstr(yborder, 0, '║')
            abc.addstr(yborder, 50, '║')
        abc.addstr(0, 0, "╔")
        abc.addstr(0, 50, "╗")
        abc.addstr(20, 0, "╚")
        abc.addstr(20, 50, "╝")
        abc.addstr(y, x, "⏹")
        abc.addstr(apy, apx, "☐")
        abc.addstr(21, 10, f"Current Delay: {speed: .5f} seconds")
        abc.refresh()
        key = abc.getch()
        if key == ord('w') and headdir != 'S':
            headdir = 'W'
        elif key == ord('s') and headdir != 'W':
            headdir = 'S'
        elif key == ord('a') and headdir != 'D':
            headdir = 'A'
        elif key == ord('d') and headdir != 'A':
            headdir = 'D'
        elif key == ord('i'):
            break
        
        if headdir == 'W':
            y -= 1 
        elif headdir == 'S':
            y += 1 
        elif headdir == 'A':
           x -= 1
        elif headdir == 'D':
            x += 1  
        time.sleep(speed)
            
        if x == apx and y == apy:
            speed /= 1.25
            apx, apy = random.randint(1, 49), random.randint(1, 19)
        if y <= 0 or y >= 20 or x <= 0 or x >= 50:
            break
curses.wrapper(main)