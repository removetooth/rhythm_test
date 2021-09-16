from glob import glob
from os.path import basename, splitext
import math
import json
import time
import sys

import pygame
pygame.init()

import constants, ui, gameplay

pygame.mixer.init()
screen = pygame.display.set_mode(ui.screensize)

clock = pygame.time.Clock()

class StateManager:
    def __init__(self):
        self.state = constants.CHART_SELECT
        self.chartSelect = ui.ChartSelectScreen()
        self.chartSelect.buttons[0].func_onclick = self.startGame
        self.gameManager = None

    def update(self, events):
        if self.state == constants.CHART_SELECT:
            self.chartSelect.buttons[0].args = [basename(self.chartSelect.songs[self.chartSelect.index]['path'])]
            self.chartSelect.update(events)
        if self.state == constants.GAMEPLAY:
            self.gameManager.update(events)
            
    def draw(self, screen):
        if self.state == constants.CHART_SELECT:
            self.chartSelect.draw(screen)
        if self.state == constants.GAMEPLAY:
            self.gameManager.draw(screen)

    def startGame(self, chart):
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        self.gameManager = gameplay.GameManager(chart)
        self.gameManager.pauseScreen.buttons[1].func_onclick = self.quitToSelection
        self.state = constants.GAMEPLAY

    def quitToSelection(self):
        self.chartSelect = ui.ChartSelectScreen()
        self.chartSelect.buttons[0].func_onclick = self.startGame
        self.state = constants.CHART_SELECT

stateManager = StateManager()

while 1:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
    stateManager.update(events)
    stateManager.draw(screen)
    pygame.display.flip()
    clock.tick()
    pygame.display.set_caption(str(int(clock.get_fps())) + " FPS")

    
