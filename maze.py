from colors import Colors as col
from bot import Bot
import copy

import pygame
import easygui
import importlib
import time

class Maze:
    def __init__(self, win, winSize, globalParametrs, mazeSize = (4, 4)):
        self.win             = win
        self.winSize         = (winSize[0] - 310, winSize[1]-10)
        self.mazeSize        = mazeSize
        self.ZP              = (5, 5)
        self.globalParametrs = globalParametrs
        self.cellSize = self.calculateCellSize(self.mazeSize, self.winSize)
        res = self.loadLUF()
        if res == None:
            self.newMaze()
        else:
            if self.loadFromFile(res) == False:
                self.newMaze()

        self.editMode = True
        self.simStartted = False
        #self.SaveToFile()
        #self.loadFromFile()

    def calculateCellSize(self, mazeSize, winSize):
        w = int(winSize[0]/mazeSize[0])
        h = int(winSize[1]/mazeSize[1])
        cellSize = min(w, h)
        return cellSize

    def installExternalWalls(self, maze):
        maze = copy.deepcopy(maze)

        for x in range(len(maze)):
            for y in range(len(maze[x])):
                if x == 0:
                    maze[x][y].walls[0] = True

                if x == len(maze) - 1:

                    maze[x][y].walls[2] = True

                if y == 0:
                    maze[x][y].walls[3] = True

                if y == len(maze[x]) - 1:
                    maze[x][y].walls[1] = True
        return maze

    def newMaze(self):
        msg = "Введите размеры поля"
        title = "Оформляем на вас кредит"
        fields = [ "Ширина (x)" , "Высота (y)" ]
        res = easygui.multenterbox (msg, title, fields)
        if res != None and len(res) == 2:
            self.mazeSize = (int(res[0]), int(res[1]))
            self.cellSize = self.calculateCellSize(self.mazeSize, self.winSize)

        self.maze = [[Cell("U", [False, False, False, False], 0, (i, j), self.cellSize, self.ZP) for i in range(self.mazeSize[0])] for j in range(self.mazeSize[1])]
        self.maze = self.installExternalWalls(self.maze)

        self.bots = [Bot((0,0), 1, self.win, self.maze, self.cellSize, self.ZP, self.globalParametrs, "BotAlgorithm")]

    def loadFromFile(self, name = None):
        if name == None:
            name = easygui.fileopenbox()
            if name == None:
                return False

        try:
            f = open(name, 'r')

        except IOError as e:
            return False

        print("Loaded from ", name)
        line = f.readline()
        #print("File saved", line[12:-1])

        line = f.readline()
        line = f.readline()
        line = f.readline()
        res = line[0:-1].split(",")
        self.mazeSize = (int(res[0]), int(res[1]))
        self.cellSize = self.calculateCellSize(self.mazeSize, self.winSize)
        self.maze = [[Cell("U", [False, False, False, False], 0, (i, j), self.cellSize, self.ZP) for i in range(self.mazeSize[0])] for j in range(self.mazeSize[1])]

        line = f.readline()
        line = f.readline()
        self.bots = []
        while True:
            line = f.readline()[0:-1]
            if line == "":
                break
            res = line.split("|")
            pos = res[0][5:].split(",")
            pos = (int(pos[0]), int(pos[1]))

            dir = int(res[1][5:])

            cubs = int(res[2][6:])

            algorithm = res[3][11:]
            self.bots.append(Bot(pos, dir, self.win, self.maze, self.cellSize, self.ZP, self.globalParametrs, algorithm))

        line = f.readline()
        for x in range(self.mazeSize[1]):
            for y in range(self.mazeSize[0]):
                line = f.readline()
                for i in range(4):
                    if int(line[i]):
                        self.maze[x][y].walls[i] = True
                    else:
                        self.maze[x][y].walls[i] = False

                self.maze[x][y].type = line[4]
                self.maze[x][y].cubs = int(line[5])

        f.close()
        self.saveLUF(name)

    def SaveToFile(self):
        name = easygui.filesavebox(default = "Maze/" + time.strftime("%Y-%m-%d %H-%M") + ".txt")
        if name == None:
            return

        print("Saved to", name)
        f = open(name, 'w')
        f.write("Maze Save - " + time.strftime("%Y-%m-%d %H-%M") + '\n')
        f.write('\n')

        f.write("Maze size:" + '\n')
        f.write(str(self.mazeSize[0]) + "," + str(self.mazeSize[1]) + '\n')
        f.write('\n')

        f.write("Bots:" + '\n')
        for i in range(len(self.bots)):
            bot = ""
            bot += "pos: "  + str(self.bots[i].pos[0]) + "," + str(self.bots[i].pos[1]) + "|"
            bot += "dir: "  + str(self.bots[i].dir) + "|"
            bot += "cubs: " + str(self.bots[i].cubs) + "|"
            bot += "algorithm: " + self.bots[i].name
            f.write(bot + '\n')
        f.write('\n')

        f.write("Cells:" + '\n')
        for x in range(len(self.maze)):
            for y in range(len(self.maze[x])):
                text = ""
                for i in range(4):
                    if self.maze[x][y].walls[i]:
                        text += "1"
                    else:
                        text += "0"

                text += self.maze[x][y].type
                text += str(self.maze[x][y].cubs)
                f.write(text + '\n')
        f.close()
        self.saveLUF(name)

    def deinstallBot(self, pos):
        for i in range(len(self.bots)):
            if self.bots[i].pos == pos:
                self.bots.pop(i)
                break

    def installBot(self, pos):
        message = "Создать новый файл автоматически?"
        title   = "Try the rainbow"
        name = None
        path = None
        answer = easygui.ynbox(message, title, ("Да", "Нет"))
        if answer == True:
            name = "Algorithm " + time.strftime("%Y-%m-%d %H-%M")
            fileName = name + ".py"
            path = "BotAlgorithms/" + fileName
            file = open(path, 'w')
            file.close()
        elif answer == False:
            res = easygui.fileopenbox()
            if res == None:
                return
            name = res.split("\\")[-1][0:-3]
            path = ""
            split = res.split("\\")
            for i in range(len(split)):
                path += split[i]
                if (i != len(split) - 1):
                    path += "/"
        else:
            return

        self.bots.append(Bot(pos, 0, self.win, self.maze, self.cellSize, self.ZP, self.globalParametrs, name))

    def run(self):
        if "needSaveFile" in self.globalParametrs:
            if self.globalParametrs["needSaveFile"]:
                self.globalParametrs["needSaveFile"] = False
                self.SaveToFile()

        if "needSwitchToEditMode" in self.globalParametrs:
            if self.globalParametrs["needSwitchToEditMode"]:
                self.globalParametrs["needSwitchToEditMode"] = False
                self.editMode = True
                self.simStartted = False

        if "needSwitchToSimulationMode" in self.globalParametrs:
            if self.globalParametrs["needSwitchToSimulationMode"]:
                self.globalParametrs["needSwitchToSimulationMode"] = False
                self.editMode = False
                self.simStartted = False

        if "needStopSimulation" in self.globalParametrs:
            if self.globalParametrs["needStopSimulation"]:
                self.globalParametrs["needStopSimulation"] = False
                self.resetBots()
                self.simStartted = False

        if "needStartSimulation" in self.globalParametrs:
            if self.globalParametrs["needStartSimulation"]:
                self.globalParametrs["needStartSimulation"] = False
                self.simStartted = True
                self.globalParametrs["simulationSpeed"] = self.globalParametrs["userSimulationSpeed"]

        if "needResetSimulation" in self.globalParametrs:
            if self.globalParametrs["needResetSimulation"]:
                self.globalParametrs["needResetSimulation"] = False
                self.resetBots()
                self.simStartted = True
                self.globalParametrs["simulationSpeed"] = self.globalParametrs["userSimulationSpeed"]

        if "needPauseSimulation" in self.globalParametrs:
            if self.globalParametrs["needPauseSimulation"]:
                self.globalParametrs["needPauseSimulation"] = False
                self.globalParametrs["simulationSpeed"] = 0

        if "needContinueSimulation" in self.globalParametrs:
            if self.globalParametrs["needContinueSimulation"]:
                self.globalParametrs["needContinueSimulation"] = False
                self.globalParametrs["simulationSpeed"] = self.globalParametrs["userSimulationSpeed"]

        if "needOpenFile" in self.globalParametrs:
            if self.globalParametrs["needOpenFile"]:
                self.globalParametrs["needOpenFile"] = False
                self.loadFromFile()

        if "needNewFile" in self.globalParametrs:
            if self.globalParametrs["needNewFile"]:
                self.globalParametrs["needNewFile"] = False
                self.newMaze()

        if self.editMode:
            self.runEdit()
        else:
            self.runSimulation()

    def resetBots(self):
        for i in range(len(self.bots)):
            self.bots[i].reset()

    def runEdit(self):
        mp = self.globalParametrs["mousePos"]
        cb = self.globalParametrs["mouseClickedButtons"]
        for x in range(len(self.maze)):
            for y in range(len(self.maze[x])):
                self.maze[x][y].runEditMode(self.win, self, self.cellSize, mp, cb, (y,x))

        for i in range(len(self.bots)):
            self.bots[i].draw()

    def runSimulation(self):
        for x in range(len(self.maze)):
            for y in range(len(self.maze[x])):
                self.maze[x][y].display(self.win, self.cellSize)

        if self.simStartted:
            for i in range(len(self.bots)):
                self.bots[i].run()
        else:
            for i in range(len(self.bots)):
                self.bots[i].draw()

    def saveLUF(self, fileName):
        res = fileName.split("\\")
        fileName = ""
        flag = False
        for i in range(len(res)):
            if res[i] == "micromause" and not(flag):
                flag = True
            elif flag:
                fileName += res[i]
                fileName += "/"

        if fileName != "":
            f = open("LUF.txt", 'w')
            f.write("Save time - " + time.strftime("%Y-%m-%d %H-%M") + '\n')
            f.write("Last used file - " + fileName[0:-1])
            f.close()

    def loadLUF(self):
        try:
            f = open("LUF.txt", 'r')

        except IOError as e:
            return None

        else:
            line = f.readline()
            line = f.readline()
            if line[-1] == '\n':
                return line[17:-1]
            else:
                return line[17:]

class Cell:
    def __init__(self, type, walls, cubsNumber, pos, Cs, ZP):
        self.type  = type # "U", "S", "F"
        self.walls = walls # [True, True, True, True] верх, право, низ, лево
        self.cubs  = cubsNumber # 0 - 4
        self.calkCorners(pos, Cs, ZP)

    def calkCorners(self, pos, Cs, ZP):
        self.corners = [((pos[0])*Cs+ZP[0], (pos[1])*Cs+ZP[1]), ((pos[0]+1)*Cs+ZP[0], (pos[1])*Cs+ZP[1]), ((pos[0]+1)*Cs+ZP[0], (pos[1]+1)*Cs+ZP[1]), ((pos[0])*Cs+ZP[0], (pos[1]+1)*Cs+ZP[1])]
        self.centre = ((pos[0])*Cs + int(Cs/2) + ZP[0], (pos[1])*Cs + int(Cs/2) + ZP[1])

    def display(self, win, Cs):
        pygame.draw.rect(win, types[self.type], (self.corners[0][0], self.corners[0][1], Cs, Cs))

        for i in range(4):
            if self.walls[i]:
                pygame.draw.line(win, col.BLACK, self.corners[i], self.corners[(i+1)%4], 3)

            else:
                pygame.draw.line(win, col.GREY5, self.corners[i], self.corners[(i+1)%4], 3)

    def runEditMode(self, win, maze, Cs, mp, cb, pos):
        distance = ((mp[0] - self.centre[0])**2 + (mp[1] - self.centre[1])**2)**0.5
        pygame.draw.rect(win, types[self.type], (self.corners[0][0], self.corners[0][1], Cs, Cs))
        if distance < Cs*0.2:
            if cb[0]:
                self.type = nextCol(self.type)
            elif cb[1]:
                self.cubs = (self.cubs + 1) % 5
            elif cb[2]:
                flag = False
                for i in range(len(maze.bots)):
                    if maze.bots[i].pos == pos: flag = True

                if flag:
                    maze.deinstallBot(pos)
                else:
                    maze.installBot(pos)

            pygame.draw.circle(win, types[nextCol(self.type)], (self.corners[0][0]+Cs/2, self.corners[0][1]+Cs/2), Cs/4)
            #pygame.draw.rect(win, types[nextCol(self.type)], (self.corners[0][0], self.corners[0][1], Cs, Cs))

        if self.cubs:
            positions = [
            (self.corners[0][0] + Cs*4/16, self.corners[0][1] + Cs*4/16, Cs*3/16, Cs*3/16),
            (self.corners[0][0] + Cs*9/16, self.corners[0][1] + Cs*4/16, Cs*3/16, Cs*3/16),
            (self.corners[0][0] + Cs*4/16, self.corners[0][1] + Cs*9/16, Cs*3/16, Cs*3/16),
            (self.corners[0][0] + Cs*9/16, self.corners[0][1] + Cs*9/16, Cs*3/16, Cs*3/16),
            ]
            for i in range(self.cubs):
                pygame.draw.rect(win, col.VIOLET, positions[i])

        for i in range(4):
            flag = False
            distance = ((mp[0] - self.corners[i][0])**2 + (mp[1] - self.corners[i][1])**2)**0.5
            distance += ((mp[0] - self.corners[(i+1)%4][0])**2 + (mp[1] - self.corners[(i+1)%4][1])**2)**0.5
            if distance < Cs*1.1:
                flag = True

            if self.walls[i] or flag:
                if cb[0] and flag:
                    self.walls[i] = not(self.walls[i])
                pygame.draw.line(win, col.BLACK, self.corners[i], self.corners[(i+1)%4], 2)
            else:
                pygame.draw.line(win, col.GREY4, self.corners[i], self.corners[(i+1)%4], 3)


types = {
"U": col.WHITE,
"S": col.GREEN,
"F": col.RED }

def nextCol(col):
    if col == "U":   return "S"
    elif col == "S": return "F"
    elif col == "F": return "U"

if __name__ == '__main__':
    pygame.init()
    pass
