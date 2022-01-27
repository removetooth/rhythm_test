#from glob import glob
#from os.path import basename, splitext
#import math
#import json
import numpy
import time
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
pygame.init()

import misc, ui, gameplay, editor
from constants import *

pygame.mixer.init()
screen = pygame.display.set_mode(ui.screensize, pygame.OPENGL | pygame.DOUBLEBUF)

clock = pygame.time.Clock()
start_time = time.time()

class StateManager:
    def __init__(self):
        self.quitToSelection()
        
    def update(self, events):
        self.manager.update(events)
            
    def draw(self, surface):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPushMatrix()
        self.manager.drawGL()
        glPopMatrix()
        glEnable(GL_BLEND)
        
        self.manager.draw(surface)

        # prepare to render the texture-mapped rectangle
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0, 0, 0, 1.0)

        # draw texture openGL Texture
        ui.surfaceToTexture( surface, screentexture )
        glBindTexture(GL_TEXTURE_2D, screentexture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-1, 1)
        glTexCoord2f(0, 1); glVertex2f(-1, -1)
        glTexCoord2f(1, 1); glVertex2f(1, -1)
        glTexCoord2f(1, 0); glVertex2f(1, 1)
        glEnd()

        glEnable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPushMatrix()
        self.manager.drawOverGL()
        glPopMatrix()

    def startGame(self, chart):
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        self.manager = gameplay.GameManager(chart)
        self.manager.pauseScreen.buttonMenu.setButtonFunc('quit', self.quitToSelection)

    def openEditor(self, chart):
        self.manager = editor.EditorManager(chart)
        self.manager.menu.setButtonFunc('return_to_menu', self.quitToSelection)
        
    def quitToSelection(self):
        self.manager = ui.ChartSelectScreen()
        self.manager.buttonMenu.setButtonFunc('start', self.startGame)
        self.manager.buttonMenu.setButtonFunc('editor', self.openEditor)

screentexture = glGenTextures(1)

stateManager = StateManager()

while 1:
    d = clock.tick(120)/(1000/120)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    stateManager.update(events)
    stateManager.draw(ui.screen_surface)
    
    pygame.display.flip()
    pygame.display.set_caption(str(int(clock.get_fps())) + " FPS")

    
