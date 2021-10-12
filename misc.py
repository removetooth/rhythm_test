import pygame

# this is fairly roundabout and can probably just be replaced with keycodes
buttons = {pygame.K_x:'a',pygame.K_c:'b',pygame.K_z:'x',pygame.K_s:'y', pygame.K_a:'l', pygame.K_d:'r',
           pygame.K_UP:'up',pygame.K_DOWN:'down',pygame.K_LEFT:'left',pygame.K_RIGHT:'right'}

sfx_blip = pygame.mixer.Sound('sfx/blip.ogg')
sfx_oops = pygame.mixer.Sound('sfx/oops.wav')
sfx_good = pygame.mixer.Sound('sfx/good.ogg')
sfx_pause = pygame.mixer.Sound('sfx/pause.ogg')
