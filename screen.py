from colors import Colors as col
from interface import Interface
from maze import Maze

from win32api import GetSystemMetrics
import pygame

class Screen:
    def __init__(self):
        self.winSize = (GetSystemMetrics(0), GetSystemMetrics(1))
        self.win     = pygame.display.set_mode(self.winSize)
        self.clock   = pygame.time.Clock()
        self.FPS     = 60

        self.globalParametrs = {
        "mousePressedButtons": pygame.mouse.get_pressed(),
        "simulationSpeed": 1,
        "userSimulationSpeed": 1,
        "FPS": self.FPS,
        }
        self.interface = Interface(self.win, self.winSize, (self.winSize[0] - 300, 0), self.globalParametrs)
        self.maze = Maze(self.win, self.winSize, self.globalParametrs)

    def run(self):
        self.win.fill(col.WHITE)

        self.updateMouseState()
        self.interface.run()
        self.maze.run()

        pygame.display.update()

    def updateMouseState(self):
        self.globalParametrs["mousePos"] = pygame.mouse.get_pos()

        MPB = pygame.mouse.get_pressed()
        MCB = [0,0,0]
        for i in range(len(MPB)):
            if self.globalParametrs["mousePressedButtons"][i] and not(MPB[i]):
                MCB[i] = 1

        self.globalParametrs["mousePressedButtons"] = MPB
        self.globalParametrs["mouseClickedButtons"] = MCB


if __name__ == '__main__':
    pygame.init()
    pass
