from glob import glob
from os.path import basename, splitext
import math
import json
import time

import pygame
pygame.init()

import constants, ui, gameplay

pygame.mixer.init()
screen = pygame.display.set_mode(ui.screensize)

clock = pygame.time.Clock()

gameManager = gameplay.GameManager(constants.chart)
pauseScreen = ui.PauseScreen()
paused = False
pygame.mixer.music.load('levels/' + constants.chart + '/music.mp3')
pygame.mixer.music.play()

# all of this should go into a game manager object later on

while 1:
    paused = not pygame.mixer.music.get_busy()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN and \
           event.key == pygame.K_ESCAPE:
            if not paused:
                paused = True
                pauseScreen.paused_at = time.time()
                pygame.mixer.stop()
                pygame.mixer.music.pause()
                constants.sfx_pause.play()
            else:
                paused = False
                pygame.mixer.music.unpause()
    if not paused:
        gameManager.update(pygame.mixer.music.get_pos(), events)
    gameManager.draw(screen)
    if paused:
        pauseScreen.update(events)
        pauseScreen.draw(screen)
    pygame.display.flip()
    clock.tick()
    pygame.display.set_caption(str(int(clock.get_fps())) + " FPS")

    
