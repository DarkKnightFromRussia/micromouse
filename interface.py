from colors import Colors as col

import copy
import pygame
import easygui

class Interface:
    def __init__(self, win, winSize, zp, globalParametrs):
        self.win             = win
        self.winSize         = winSize
        self.ZP              = zp
        self.globalParametrs = globalParametrs

        self.font1           = pygame.font.SysFont('arial', 36)
        self.font2           = pygame.font.SysFont('arial', 15)
        self.makeButtonsList()

        self.simStartted = False
        self.simPaused = False
        self.editMode = True

    def run(self):
        pygame.draw.rect(self.win, col.WHITE, (self.ZP[0], self.ZP[1], self.winSize[0] - self.ZP[0], self.winSize[1]))
        mp = self.globalParametrs["mousePos"]
        cb = self.globalParametrs["mouseClickedButtons"]

        if self.buttons["New file"].run(mp, cb):
            self.globalParametrs["needNewFile"] = True
            self.editMode = True
            self.globalParametrs["needSwitchToEditMode"] = True
            self.globalParametrs["needStopSimulation"] = True

        if self.buttons["Save file"].run(mp, cb):
            self.globalParametrs["needSaveFile"] = True
            self.globalParametrs["needStopSimulation"] = True

        if self.buttons["Open"].run(mp, cb):
            self.globalParametrs["needOpenFile"] = True
            self.editMode = True
            self.globalParametrs["needSwitchToEditMode"] = True
            self.globalParametrs["needStopSimulation"] = True

        if self.buttons["Stop"].run(mp, cb):
            self.simStartted = False
            self.globalParametrs["needStopSimulation"] = True

        #Режим редактирования/симуляции
        if self.editMode:
            if self.buttons["Simulation"].run(mp, cb):
                self.editMode = False
                self.simStartted = False
                self.simPaused = False
                self.globalParametrs["needSwitchToSimulationMode"] = True
        else:
            if self.buttons["Edit"].run(mp, cb):
                self.editMode = True
                self.globalParametrs["needSwitchToEditMode"] = True
                self.globalParametrs["needStopSimulation"] = True

        #кнопка поставить на паузу/продолжить
        if self.simPaused:
            if self.buttons["Continue"].run(mp, cb):
                self.simPaused = False
                self.globalParametrs["needContinueSimulation"] = True
        else:
            if self.buttons["Pause"].run(mp, cb):
                self.simPaused = True
                self.globalParametrs["needPauseSimulation"] = True

        #Кнопка старт/рестарт
        if self.simStartted:
            if self.buttons["Reset"].run(mp, cb):
                self.simPaused = False
                self.globalParametrs["needResetSimulation"] = True
        else:
            if self.buttons["Start"].run(mp, cb):
                self.simStartted = True
                self.simPaused = False
                self.globalParametrs["needStartSimulation"] = True

    def makeButtonsList(self):
        self.buttons  = {}
        self.buttons["New file"]   = Button(self.win, calkPos(self.ZP, (10,10)),  (60,25), "New file",   self.font2)
        self.buttons["Open"]       = Button(self.win, calkPos(self.ZP, (10,40)),  (60,25), "Open",       self.font2)
        self.buttons["Save file"]  = Button(self.win, calkPos(self.ZP, (10,70)),  (60,25), "Save",       self.font2)
        self.buttons["Stop"]       = Button(self.win, calkPos(self.ZP, (220,40)), (60,25), "Stop",       self.font2)

        self.buttons["Edit"]       = Button(self.win, calkPos(self.ZP, (80,10)),  (60,25), "Edit",       self.font2)
        self.buttons["Simulation"] = Button(self.win, calkPos(self.ZP, (80,10)),  (60,25), "Simulation", self.font2)

        self.buttons["Pause"]      = Button(self.win, calkPos(self.ZP, (150,10)), (60,25), "Pause",      self.font2)
        self.buttons["Continue"]   = Button(self.win, calkPos(self.ZP, (150,10)), (60,25), "Continue",   self.font2)

        self.buttons["Start"]      = Button(self.win, calkPos(self.ZP, (220,10)), (60,25), "Start",      self.font2)
        self.buttons["Reset"]      = Button(self.win, calkPos(self.ZP, (220,10)), (60,25), "Reset",      self.font2)

        #self.buttons["Pause"] = ButtonSwitch(self.win, calkPos(self.ZP, (150,10)), (60,25), "Pause", "Continue", self.font2)
        #self.buttons["Start"] = ButtonSwitch(self.win, calkPos(self.ZP, (220,10)), (60,25), "Start", "Reset",     self.font2)
        #self.buttons[""] =

class Button:
    def __init__(self, win, pos, size, text, font):
        self.win  = win
        self.pos  = pos
        self.size = size
        text = font.render(text, True, col.BLACK)

        self.surf1 = pygame.Surface(self.size)
        self.surf1.fill(col.WHITE)
        self.surf1.blit(text, ((size[0] - text.get_width())/2, (size[1] - text.get_height())/2))
        pygame.draw.rect(self.surf1, col.GREY2, (0, 0, self.size[0], self.size[1]), 3)

        self.surf2 = pygame.Surface(self.size)
        self.surf2.fill(col.GREY5)
        self.surf2.blit(text, ((size[0] - text.get_width())/2, (size[1] - text.get_height())/2))
        pygame.draw.rect(self.surf2, col.BLACK, (0, 0, self.size[0], self.size[1]), 3)

    def run(self, mp, pb):
        if mp[0] > self.pos[0] and mp[0] < self.pos[0] + self.size[0] and mp[1] > self.pos[1] and mp[1] < self.pos[1] + self.size[1]:
            self.win.blit(self.surf2, self.pos)
            if pb[0]:
                self.pt = pygame.time.get_ticks()
                return True
        else:
            self.win.blit(self.surf1, self.pos)

class ButtonSwitch:
    def __init__(self, win, pos, size, text1, text2, font):
        self.win  = win
        self.pos  = pos
        self.size = size
        self.status = 0
        text1 = font.render(text1, True, col.BLACK)
        text2 = font.render(text2, True, col.BLACK)

        self.surf1 = []
        self.surf1.append(pygame.Surface(self.size))
        self.surf1[0].fill(col.WHITE)
        self.surf1[0].blit(text1, ((size[0] - text1.get_width())/2, (size[1] - text1.get_height())/2))
        pygame.draw.rect(self.surf1[0], col.GREY2, (0, 0, self.size[0], self.size[1]), 3)

        self.surf1.append(pygame.Surface(self.size))
        self.surf1[1].fill(col.WHITE)
        self.surf1[1].blit(text2, ((size[0] - text2.get_width())/2, (size[1] - text2.get_height())/2))
        pygame.draw.rect(self.surf1[1], col.GREY2, (0, 0, self.size[0], self.size[1]), 3)

        self.surf2 = []
        self.surf2.append(pygame.Surface(self.size))
        self.surf2[0].fill(col.GREY5)
        self.surf2[0].blit(text1, ((size[0] - text1.get_width())/2, (size[1] - text1.get_height())/2))
        pygame.draw.rect(self.surf2[0], col.BLACK, (0, 0, self.size[0], self.size[1]), 3)

        self.surf2.append(pygame.Surface(self.size))
        self.surf2[1].fill(col.GREY5)
        self.surf2[1].blit(text2, ((size[0] - text2.get_width())/2, (size[1] - text2.get_height())/2))
        pygame.draw.rect(self.surf2[1], col.BLACK, (0, 0, self.size[0], self.size[1]), 3)

    def run(self, mp, pb, status = 0):

        if mp[0] > self.pos[0] and mp[0] < self.pos[0] + self.size[0] and mp[1] > self.pos[1] and mp[1] < self.pos[1] + self.size[1]:
            self.win.blit(self.surf2[self.status], self.pos)
            if pb[0]:
                self.status = (self.status + 1) % 2
                return True
        else:
            self.win.blit(self.surf1[self.status], self.pos)

def calkPos(ZP, pos):
    return (ZP[0] + pos[0], ZP[1] + pos[1])


if __name__ == '__main__':
    pygame.init()
    pass
