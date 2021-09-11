from glob import glob
from os.path import basename, splitext
import math
import json 

import pygame
pygame.init()

import constants, ui, gameplay

pygame.mixer.init()
screen = pygame.display.set_mode(ui.screensize)

clock = pygame.time.Clock()

gameManager = gameplay.GameManager(constants.chart)
pygame.mixer.music.load('levels/' + constants.chart + '/music.mp3')
pygame.mixer.music.play()

# all of this should go into a game manager object later on

while pygame.mixer.music.get_busy():
    gameManager.update(pygame.mixer.music.get_pos())
    gameManager.draw(screen)
    pygame.display.flip()
    clock.tick()
    #pygame.display.set_caption(str(clock.get_fps()))

    
