from multiprocessing import Process, Pipe
import importlib
import pygame
import time


class UserBot:
    def __init__(self, pos, dir, maze, OC, IC):
        self.maze     = maze
        self.pos      = pos
        self.dir      = dir
        self.startDir = self.dir
        self.OC       = OC
        self.IC       = IC

    def allSensors(self):
        return (self.leftDS(), self.frontDS(), self.rightDS(), self.gyroSensor(), self.colorSensor())

    def leftDS(self):
        return self.maze[self.pos[1]][self.pos[0]].walls[(self.dir - 1)%4]

    def rightDS(self):
        return self.maze[self.pos[1]][self.pos[0]].walls[(self.dir + 1)%4]

    def frontDS(self):
        return self.maze[self.pos[1]][self.pos[0]].walls[self.dir]

    def gyroSensor(self):
        return (self.dir - self.startDir) % 4

    def colorSensor(self):
        return self.maze[self.pos[1]][self.pos[0]].type

    def turnLeft(self):
        self.dir = (self.dir - 1)%4
        self.OC.send("turnLeft")

        while True:
            if self.IC.poll():
                return self.IC.recv()

    def turnRight(self):
        self.dir = (self.dir + 1)%4
        self.OC.send("turnRight")

        while True:
            if self.IC.poll():
                return self.IC.recv()

    def driveForward(self):
        self.OC.send("driveForward")
        while True:
            if self.IC.poll():
                res = self.IC.recv()
                if res:
                    dPos = FMCBD(self.dir)
                    self.pos = (self.pos[0] + dPos[0], self.pos[1] + dPos[1])
                return res

class Bot:
    def __init__(self, pos, dir, win, maze, Cs, ZP, globalParametrs, name):
        self.pos    = pos
        self.oldPos = self.pos
        self.stPos  = self.pos
        self.dir    = dir
        self.oldDir = self.dir
        self.stDir  = self.dir
        self.cubs  = 0
        self.win    = win
        self.maze   = maze
        self.Cs     = Cs
        self.ZP     = ZP
        self.globalParametrs = globalParametrs
        self.IC1, self.OC1 = Pipe()
        self.IC2, self.OC2 = Pipe()
        self.action = False
        self.executionPart = 0

        self.prepareImages()

        self.name = name
        self.algorithmIsExecuting = False
        self.updateIsPossible = False

    def run(self):
        if not(self.algorithmIsExecuting):
            self.algorithmIsExecuting = True

            algorithm = importlib.import_module(self.name).run
            bot = UserBot(self.pos, self.dir, self.maze, self.OC1, self.IC2)

            self.proc = Process(target = algorithm, args = (bot, ))
            self.proc.start()

        if self.IC1.poll():
            res = self.IC1.recv()
            self.action = res

        if self.action != False:
            if self.action == "driveForward":
                self.driveForward()
            elif self.action == "turnLeft":
                self.turnLeft()
            elif self.action == "turnRight":
                self.turnRight()

        else:
            x = int(self.Cs*self.pos[0] + self.Cs/2 - self.preparedImages[self.dir][self.cubs].get_width()/2 + self.ZP[0])
            y = int(self.Cs*self.pos[1] + self.Cs/2 - self.preparedImages[self.dir][self.cubs].get_height()/2 + self.ZP[1])
            self.win.blit(self.preparedImages[self.dir][self.cubs], (x, y))

    def draw(self):
        x = int(self.Cs*self.pos[0] + self.Cs/2 - self.preparedImages[self.dir][self.cubs].get_width()/2 + self.ZP[0])
        y = int(self.Cs*self.pos[1] + self.Cs/2 - self.preparedImages[self.dir][self.cubs].get_height()/2 + self.ZP[1])
        self.win.blit(self.preparedImages[self.dir][self.cubs], (x, y))

    def reset(self):
        if self.algorithmIsExecuting:
            self.pos = self.stPos
            self.oldPos = self.stPos
            self.dir = self.stDir
            self.oldDir = self.stDir
            self.algorithmIsExecuting = False
            self.executionPart = 0
            self.proc.terminate()

    def prepareImages(self):
        self.startImages = []
        for i in range(5):
            fileName = "BotImages/" + str(i) + "_Cube.png"
            self.startImages.append(pygame.image.load(fileName))
            self.startImages[i].set_colorkey((255, 255, 255))

        self.preparedImages = []
        for i in range(4):
            self.preparedImages.append([])
            for j in range(5):
                size = int(self.Cs/1.5)
                image = pygame.transform.rotate(self.startImages[j], i*-90)
                image = pygame.transform.scale(image, (size, size))
                image.set_colorkey((255, 255, 255))
                self.preparedImages[i].append(image)

    # анимации передвижения и вращения бота
    def driveForward(self):
        if self.executionPart == 0:
            if self.maze[self.pos[1]][self.pos[0]].walls[self.dir]:
                self.action = False
                self.OC2.send(False)
                return
            dPos = FMCBD(self.dir)
            self.oldPos = self.pos
            self.pos = (self.pos[0] + dPos[0], self.pos[1] + dPos[1])

        self.executionPart += 2 * self.globalParametrs["simulationSpeed"] / self.globalParametrs["FPS"]

        x, y = (0, 0)
        dx, dy = (0, 0)
        if self.executionPart >= 1:
            self.executionPart = 0
            self.action = False
            self.OC2.send(True)
            x = self.Cs*self.pos[0] + self.Cs/2 + self.ZP[0]
            y = self.Cs*self.pos[1] + self.Cs/2 + self.ZP[1]
        else:
            x = self.Cs*self.oldPos[0] + self.Cs/2 + self.ZP[0]
            y = self.Cs*self.oldPos[1] + self.Cs/2 + self.ZP[1]
            dx = (self.pos[0] - self.oldPos[0])*self.executionPart*self.Cs
            dy = (self.pos[1] - self.oldPos[1])*self.executionPart*self.Cs

        serf = self.preparedImages[self.dir][self.cubs]
        rect = serf.get_rect(center = (x + dx, y + dy))
        self.win.blit(serf, rect)

    def turnRight(self):
        if self.executionPart == 0:
            self.oldDir = self.dir
            self.dir = (self.dir + 1)%4

        self.executionPart += 4 * self.globalParametrs["simulationSpeed"] / self.globalParametrs["FPS"]
        angle = self.executionPart * 90 * -1
        if self.executionPart >= 1:
            angle = -90
            self.executionPart = 0
            self.action = False
            self.OC2.send(True)

        serf = self.preparedImages[self.oldDir][self.cubs]

        x = int(self.Cs*self.pos[0] + self.Cs/2 + self.ZP[0])
        y = int(self.Cs*self.pos[1] + self.Cs/2 + self.ZP[1])
        serf = pygame.transform.rotate(serf, angle)
        serf.set_colorkey((255, 255, 255))
        rect = serf.get_rect(center = (x,y))
        self.win.blit(serf, rect)

    def turnLeft(self):
        if self.executionPart == 0:
            self.oldDir = self.dir
            self.dir = (self.dir - 1)%4

        self.executionPart += 4 * self.globalParametrs["simulationSpeed"] / self.globalParametrs["FPS"]
        angle = self.executionPart * 90
        if self.executionPart >= 1:
            angle = 90
            self.executionPart = 0
            self.action = False
            self.OC2.send(True)

        serf = self.preparedImages[self.oldDir][self.cubs]

        x = int(self.Cs*self.pos[0] + self.Cs/2 + self.ZP[0])
        y = int(self.Cs*self.pos[1] + self.Cs/2 + self.ZP[1])
        serf = pygame.transform.rotate(serf, angle)
        serf.set_colorkey((255, 255, 255))
        rect = serf.get_rect(center = (x,y))
        self.win.blit(serf, rect)


def FMCBD(dir):
    dx = 0
    dy = 0
    if dir == 0:   dy = -1
    elif dir == 1: dx = 1
    elif dir == 2: dy = 1
    elif dir == 3: dx = -1

    return (dx, dy)

if __name__ == "__main__":
    pygame.init()
    pass
