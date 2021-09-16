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
        self.manager = ui.ChartSelectScreen()
        self.manager.buttons[0].func_onclick = self.startGame
        
    def update(self, events):
        self.manager.update(events)
            
    def draw(self, screen):
        self.manager.draw(screen)

    def startGame(self, chart):
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        self.manager = gameplay.GameManager(chart)
        self.manager.pauseScreen.buttons[1].func_onclick = self.quitToSelection
        
    def quitToSelection(self):
        self.manager = ui.ChartSelectScreen()
        self.manager.buttons[0].func_onclick = self.startGame

stateManager = StateManager()

while 1:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
    stateManager.update(events)
    stateManager.draw(screen)
    pygame.display.flip()
    clock.tick(120)
    pygame.display.set_caption(str(int(clock.get_fps())) + " FPS")

    
