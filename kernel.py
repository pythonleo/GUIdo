# kernel.py
# Core of our OS

import pygame, sys, random, time, io
from math import *
from contextlib import redirect_stdout
from enum import Enum

width, height = 1024, 768

def pwd(working_dir, args):
    print(working_dir, end='')

def ls(working_dir, args):
    files = open("files.img", 'r+')
    lines = files.read().strip('\0').split('\n')
    for i, line in enumerate(lines):
        if line == "!LOC=%s" % working_dir:
            print(lines[i + 1].strip('!FNAME='), end='')

def cat(working_dir, args):
    if not args:
        print("Missing argument. Usage: cat <filename(s)>", end='')
        return
    for target in args:
        files = open("files.img", 'r+')
        lines = files.read().strip('\0').split('\n')
        contents = []
        for i, line in enumerate(lines):
            if line == '!LOC=%s' % working_dir \
                and lines[i + 1] == '!FNAME=%s' % target:
                    for i in range(i+2, len(lines)):
                        if lines[i] and lines[i][0] == '!': break
                        contents.append(lines[i])
                    break
        else:
            print("cat: %s: no such file or directory" % target, end='')
        print(''.join(contents))
        files.close()

def rm(working_dir, args):
    files = open("files.img", 'r+')
    to_be_written = []
    target = args[0]
    lines = files.read().strip('\0').split('\n')
    write_or_not = True
    for i, line in enumerate(lines):
        if write_or_not:
            if line == '!FNAME=%s' % target \
           and lines[i-1] == '!LOC=%s' % working_dir:
                write_or_not = False
                del to_be_written[-1]
        else:
            if line and line[0] == '!':
                write_or_not = True
        if write_or_not:
            to_be_written.append(line)
    files.close()
    fw = open("files.img", 'w+')
    fw.write('\n'.join(to_be_written))
    fw.close()

def calc(working_dir, args):
    expr = input()
    while expr != 'q':
        result = None
        try:
            result = eval(expr)
        except ZeroDivisionError:
            print("Don't divide by zero!", end='')
        except SyntaxError:
            print("Your expression doesn't seem to be valid.", end='')
        except:
            print("This expression doesn't seem to work.", end='')
        if result:
            print(result, end='')
        expr = input()

def vis(working_dir, args):
    if not args:
        print("Missing argument. Usage: vis <filename>", end='\r')
    while True:
        cmd = input()
        print(cmd, end='\r')
        if cmd == "i":
            rm(working_dir, args[0])
            files = open("files.img", 'r+')
            files.write("!FNAME=" + args[0] + "\n")
            files.write("!LOC=" + working_dir + "\n")
            while True:
                line = input()
                print(line, end = '\r')
                if line == ".":
                    break
                line += '\n'
                files.write(line)
            files.close()
        elif cmd == "q":
            return
        else:
            print("?", end='\r')

class Pic(object):
    def __init__(self, fileName):
        img = pygame.image.load(fileName)
        self.img = pygame.transform.scale(img, (width, height))
        self.x, self.y = 0, 0
        self.w, self.h = self.img.get_size()
    def draw(self, screen, speed = 5):
        screen.blit(self.img, (self.x, self.y), (0, 0, self.w, self.h))
        pygame.draw.rect(screen, (0, 255, 0), (0, 0, speed * 8, 8), 0)
    def getPixelGrid(self, x0, y0, sideLen, pixelGrid):
        n = sideLen // 2
        for y in range(-n, n + 1):
            for x in range(-n, n + 1):
                pixelGrid[y + n][x + n] = self.img.get_at((x + x0, y + y0))

class Kernel:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Winnux 58")
        self.clock = pygame.time.Clock()
        self.raster = pygame.font.Font("res/Perfect_DOS_VGA_437.ttf", 15)
        self.speed = 5
        self.mousePos = (0, 0)
        self.apps = []
        self.appID = 0
        self.dialogs = []
        self.dialogID = 0
    def launch(self):
        for app in self.apps:
            app.draw(self.screen)
        for dialog in self.dialogs:
            try:
                dialog.draw(self.screen)
            except:
                pass
        pygame.display.update()
        self.clock.tick(50)
    def addApp(self, app):
        app.appID = len(self.apps)
        self.apps.append(app)
    def addDialog(self, dialog):
        dialog.dialogID = len(self.dialogs)
        dialog.closeBtn = Secret((dialog.x + 357, dialog.y + 6, 17, 16), dialog.dialogID)
        self.dialogs.append(dialog)
    def keyUp(self, key):
        self.apps[self.appID].keyUp(key)
    def keyDown(self, key):
        self.apps[self.appID].keyDown(key)
    def mouseDown(self, pos, button):
        self.apps[self.appID].mouseDown(pos, button)
        try:
            self.dialogs[self.dialogID].mouseDown(pos, button)
        except:
            pass
        print(event.pos)
    def mouseUp(self, pos, button):
        self.apps[self.appID].mouseUp(pos, button)
    def mouseMotion(self, pos):
        self.apps[self.appID].mouseMotion(pos)

class App:
    def __init__(self, picName):
        self.pic = Pic(picName)
        self.appID = 0
        self.btnList = []
        self.tooltipList = []
        self.txtField = TxtField(0, 0, 0, 0)
        self.txtFieldEnabled = False
        self.canvas = pygame.Surface((width, height - 60))
        self.canvasEnabled = False
        self.secretList = []
    def draw(self, screen):
        if framework.appID != self.appID:
            return
        screen.blit(self.pic.img, (0, 0))
        for button in self.btnList:
            button.draw(screen)
        for tooltip in self.tooltipList:
            tooltip.draw(screen)
        if self.txtFieldEnabled:
            self.txtField.content = self.txtField.wrap(self.txtField.txtBuffer)
            self.txtField.content = self.txtField.content[-self.txtField.h:]
            self.txtField.draw(screen, self.txtField.content)
        if self.canvasEnabled:
            if self.appID == snake.appID:
                snakeGame.draw(self.canvas)
                snakeGame.move()
            framework.screen.blit(self.canvas, (0, 60))
    def addButton(self, b):
        self.btnList.append(b)
    def addTooltip(self, txt, font, x, y, c, rect):
        tt = Tooltip(txt, font, x, y, c, rect)
        self.txtList.append(tt)
    def enableTxtField(self, x, y, w, h):
        if self.canvasEnabled:
            print("Only one of either the text field or the canvas can be enabled in an App.")
            return
        self.txtFieldEnabled = True
        self.txtField.x, self.txtField.y = x, y
        self.txtField.w, self.txtField.h = w, h
    def enableCanvas(self):
        if self.txtFieldEnabled:
            print("Only one of either the text field or the canvas can be enabled in an App.")
            return
        self.canvasEnabled = True
    def mouseDown(self, pos, button):
        for btn in self.btnList:
            btn.mouseDown(pos, button)
        for secret in self.secretList:
            secret.mouseDown(pos, button)
    def mouseUp(self, pos, button):
        for button in self.btnList:
            button.mouseUp(pos, button)
    def mouseMotion(self, pos):
        framework.mousePos = pos
        for btn in self.btnList:
            btn.mouseMove(pos)
    def keyUp(self, key):
        if self.txtFieldEnabled:
            self.txtField.keyUp(key)
    def keyDown(self, key):
        if self.txtFieldEnabled:
            self.txtField.keyDown(key)
        if self.canvasEnabled:
            if self.appID == snake.appID:
                snakeGame.keyDown(key)

class Button:
    def __init__(self, picFile, x, y, appID, **txt):
        self.img = pygame.image.load(picFile).convert()
        self.w, self.h = self.img.get_width() // 3, self.img.get_height()
        self.x, self.y = x, y
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.status = 0
        self.appID = appID
        self.txt = txt
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y),
                    (self.status * self.rect.w, 0,
                     self.rect.w, self.rect.h))
        if self.txt:
            screen.blit(self.txt["font"].render(self.txt["content"], True, (0,0,0)), \
                        (self.x + self.w // 2 - 4 * len(self.txt["content"]), self.y + self.h // 2 - 8))
    def mouseDown(self, pos, button):
        if self.rect.collidepoint(pos):
            self.status = 2
    def mouseUp(self, pos, button):
        self.status = 0
        if not self.rect.collidepoint(pos):
            return
        framework.apps[self.appID].pic.draw(framework.screen, framework.speed)
        framework.appID = self.appID
    def mouseMove(self, pos):
        if self.rect.collidepoint(pos):
            self.status = 1
        else:
            self.status = 0

class Tooltip:
    def __init__(self, txt, font, x, y, c, rect):
        self.txt = txt
        self.img = font.render(txt, True, c)
        self.x, self.y = x, y
        self.c = c
        self.rect = pygame.Rect(rect)
    def draw(self, screen):
        if self.rect.collidepoint(framework.mousePos):
            screen.blit(self.img, (self.x, self.y))

class TxtField:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.pwd = '/'
        self.placeholder = ['%s# ' % self.pwd]
        self.txtBuffer = []
        self.content = []
        self.caps = { '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', '\'': '"', ',': '<', '.': '>', '/': '?', 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z' }
        self.shift, self.capsLock = False, False
        self.raster = pygame.font.Font("res/Perfect_DOS_VGA_437.ttf", 28)
    def wrap(self, txtBuffer):
        lines = []
        ptr = 0
        temp = self.placeholder[ptr]
        for i in range(len(txtBuffer)):
            if txtBuffer[i] == '\n':
                lines.append(temp)
                ptr += 1
                temp = self.placeholder[ptr]
            elif txtBuffer[i] == '\r':
                lines.append(temp)
                temp = ''
            elif (i != 0 and i % self.w == 0):
                lines.append(temp)
                temp = ""
            else:
                temp += txtBuffer[i]
        lines.append(temp)
        return lines
    def draw(self, screen, lines, c = (255, 255, 255), y = 0):
        for line in lines:
            img = self.raster.render(line, True, c)
            screen.blit(img, (0, y))
            y += 30

    def cd(self, dir_name):
        self.pwd += dir_name + '/'

    def exec_cmd(self, on_scr):
        cmd = on_scr.split()
        try: main = cmd.pop(0)
        except: main = None
        output = io.StringIO()
        with redirect_stdout(output):
            sys.stdin = output
            if main:
                if main == 'cd': self.cd(cmd[0])
                else:
                    #print("%s('%s', %s)" % (main, self.pwd, str(cmd)))
                    exec("%s('%s', %s)" % (main, self.pwd, str(cmd)))
            else: print("%s: command not found" % on_scr, end='')
        sys.stdin = sys.__stdin__
        self.txtBuffer.append('\r')
        self.txtBuffer += list(output.getvalue().rstrip('\n'))
        self.placeholder.append('%s# ' % self.pwd)
    def keyUp(self, key):
        if key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
            self.shift = False
        elif key == pygame.K_CAPSLOCK:
            self.capsLock = 1 - self.capsLock
    def keyDown(self, key):
        if key == pygame.K_BACKSPACE:
            if (self.txtBuffer and self.txtBuffer[-1] != '\n') or not self.txtBuffer:
                try: self.txtBuffer.pop()
                except: pass
        elif key == pygame.K_RETURN:
            cmd = ''
            i = -1
            while len(self.txtBuffer) > - i - 1 and self.txtBuffer[i] != '\n':
                cmd = self.txtBuffer[i] + cmd
                i -= 1
            self.exec_cmd(cmd)
            self.txtBuffer.append('\n')
        elif key == pygame.K_TAB:
            for i in range(4):
                self.txtBuffer.append(' ')
        elif key == pygame.K_LSHIFT or key == pygame.K_RSHIFT:
            self.shift = True
        elif key == pygame.K_CAPSLOCK:
            self.capsLock = 1 - self.capsLock
        else:
            if 32 <= key <= 126:
                if (key == 39 or 44 <= key <= 57 or key == 59 or key == 61 or key == 96 or 91 <= key <= 93) and self.shift:
                    self.txtBuffer.append(self.caps[chr(key)])
                elif 97 <= event.key <= 122 and (self.shift or self.capsLock):
                    self.txtBuffer.append(self.caps[chr(key)])
                else:
                    self.txtBuffer.append(chr(key))

class Secret:
    def __init__(self, rect, dialogID):
        self.rect = pygame.Rect(rect)
        self.dialogID = dialogID
    def mouseDown(self, pos, button):
        if self.rect.collidepoint(pos):
            framework.dialogs.pop()

class DlgStatus(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2

class Dialog:
    def __init__(self, title, content, status=DlgStatus.INFO):
        self.img = pygame.image.load("res/dialog/dialog.png")
        self.icon = pygame.transform.scale(pygame.image.load("res/dialog/" + str(status) + ".bmp"), (32, 32))
        self.icon.set_colorkey((255, 0, 255))
        self.raster = pygame.font.Font("res/Perfect_DOS_VGA_437.ttf", 16)
        self.title = self.raster.render(title, True, (255, 255, 255))
        self.content = self.wrap(content, 35)
        self.dialogID = 0
        self.w, self.h = self.img.get_size()
        self.x, self.y = 322, 284
        self.closeBtn = None
    def wrap(self, txt, w):
        processed = []
        temp = ""
        for i in range(txt.__len__()):
            if i != 0 and i % w == 0:
                processed.append(self.raster.render(temp, True, (0, 0, 0)))
                temp = ""
            temp += txt[i]
        processed.append(self.raster.render(temp, True, (0, 0, 0)))
        return processed
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        screen.blit(self.title, (self.x + 10, self.y + 6))
        screen.blit(self.icon, (self.x + 30, self.y + 90))
        for i in range(len(self.content)):
            screen.blit(self.content[i], (self.x + 80, self.y + 35 + i * 16))
    def mouseDown(self, pos, button):
        self.closeBtn.mouseDown(pos, button)

class SnakeGame:
    def __init__(self):
        self.tileWidth = 32
        self.x0, self.y0 = 192, 144
        self.snakeLen = 1
        self.snakePos = []
        self.direction = 0
        self.speedX = (1, 0, -1, 0)
        self.speedY = (0, 1, 0, -1)
        self.sx, self.sy = 0, 0
        self.ix, self.iy = random.randint(0, 19), random.randint(0, 14)
        self.lost = 0
        self.bigFont = pygame.font.Font("res/Perfect_DOS_VGA_437.ttf", 100)
        self.smallFont = pygame.font.Font("res/Perfect_DOS_VGA_437.ttf", 60)
        self.bg = pygame.Surface((640, 480))
        self.bg.fill((255, 255, 255))
        self.gameOver = self.bigFont.render("Game Over!", True, (255, 255, 255))
        self.restart = self.smallFont.render("PRESS R TO RESTART", True, (255, 255, 255))
    def draw(self, canvas):
        canvas.fill((40, 40, 40))
        if self.lost == 1:
            canvas.blit(self.gameOver, (250, 200))
            canvas.blit(self.restart, (230, 300))
            return
        canvas.blit(self.bg, (self.x0, self.y0))
        for pos in self.snakePos[-self.snakeLen:]:
            pygame.draw.rect(canvas, (60, 110, 5), (self.x0 + pos[0] * self.tileWidth, self.y0 + pos[1] * self.tileWidth, self.tileWidth, self.tileWidth))
        pygame.draw.rect(canvas, (190, 30, 50), (self.x0 + self.ix * self.tileWidth, self.y0 + self.iy * self.tileWidth, self.tileWidth, self.tileWidth))
    def move(self):
        if self.lost == 1:
            return
        self.sx = (self.sx + self.speedX[self.direction]) % 20
        self.sy = (self.sy + self.speedY[self.direction]) % 15
        if (self.sx, self.sy) in self.snakePos[-self.snakeLen:]:
            self.lost = 1
        self.snakePos.append((self.sx, self.sy))
        if self.sx == self.ix and self.sy == self.iy:
            self.ix, self.iy = random.randint(0, 19), random.randint(0, 14)
            self.snakeLen += 1
    def keyDown(self, key):
        if key == pygame.K_UP:
            self.direction = 3
        if key == pygame.K_DOWN:
            self.direction = 1
        if key == pygame.K_LEFT:
            self.direction = 2
        if key == pygame.K_RIGHT:
            self.direction = 0
        if key == pygame.K_r and self.lost == 1:
            self.snakeLen = 1
            self.snakePos = []
            self.sx, self.sy = 0, 0
            self.ix, self.iy = random.randint(0, 19), random.randint(0, 14)
            self.lost = 0


framework = Kernel()
bg = App("res/clouds.jpg")
term = App("res/blank.jpg")
termCtrl = TxtField(0, 0, 80, 20)
snake = App("res/blank.jpg")
snake.enableCanvas()
snakeGame = SnakeGame()
framework.appID = bg.appID
framework.addApp(bg)
framework.addApp(term)
framework.addApp(snake)
framework.addDialog(Dialog("Hey there!", "Welcome to Winnux 58!"))
bg.addButton(Button("res/button/txt_btn.bmp", 20, 20, term.appID, font=framework.raster, content="TERMINAL"))
bg.addButton(Button("res/button/txt_btn.bmp", 20, 60, snake.appID, font=framework.raster, content="SNAKE"))
term.addButton(Button("res/button/txt_btn.bmp", width // 2 - 35, 20, bg.appID, font=framework.raster, content="CLOSE"))
snake.addButton(Button("res/button/txt_btn.bmp", width // 2 - 35, 20, bg.appID, font=framework.raster, content="CLOSE"))
term.enableTxtField(0, 0, 80, 20)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            framework.keyDown(event.key)
        elif event.type == pygame.KEYUP:
            framework.keyUp(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            framework.mouseDown(event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            framework.mouseUp(event.pos, event.button)
        elif event.type == pygame.MOUSEMOTION:
            framework.mouseMotion(event.pos)
    framework.launch()
