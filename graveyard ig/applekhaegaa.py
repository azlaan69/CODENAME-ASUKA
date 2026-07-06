import curses
import time
import random
def main(abc):
    curses.curs_set(0)
    abc.nodelay(True)
    y = 10
    x = 25
    speed = 0.3
    stage = 0
    headdir = 'W'
    vh = 0
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
        abc.addstr(y, x, "H")
        abc.addstr(apy, apx, "O")
        abc.addstr(21, 10, f"Current Delay: {speed: .5f} seconds")
        if stage >= 1.0:
            abc.addstr(22, 10, f"STAGE {stage}")
            abc.addstr(24, 10, f"TICK: {vh}")
        
        key = abc.getch()
        if stage >= 1.0:
            if vh == 0:
                vh += 1
            if time.time() - timer >= 1.0:
                vh += 1
                timer = time.time()
                if vh == 5:
                    apx, apy = random.randint(1, 49), random.randint(1, 19)
            if vh == 1 or vh == 3:
                for j in range(1, 50):
                    abc.addstr(apy, j, "━")
                    abc.addstr(apy, apx, "O", curses.A_BLINK)
            elif vh == 2 or vh == 4:
                for k in range(1, 20):
                    abc.addstr(k, apx, "┃")
                    abc.addstr(apy, apx, "O", curses.A_BLINK)
            if vh == 6:
                abc.addstr(23, 10, "ATTACK")
            if vh == 7:
                vh = 1
        if x == apx and y == apy:
            speed /= 1.25
            apx, apy = random.randint(1, 49), random.randint(1, 19)
            stage += 0.25
            timer = time.time()
        
        abc.refresh()
        
        if key == ord('w'):
            headdir = 'W'
        elif key == ord('s'):
            headdir = 'S'
        elif key == ord('a'):
            headdir = 'A'
        elif key == ord('d'):
            headdir = 'D'
        if key == ord('t'):
            x, y = apx, apy+1
            headdir = 'W'
        elif key == ord('i'):
            break
        if y <= 0 or y >= 20 or x <= 0 or x >= 50:
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
            
curses.wrapper(main)