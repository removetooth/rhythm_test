import pygame

chart_folder = "levels/test"

# this is fairly roundabout and can probably just be replaced with keycodes
buttons = {pygame.K_z:'a',pygame.K_x:'b',pygame.K_c:'x',pygame.K_v:'y'}

ui_screensize = [640,480]
ui_colorkey = [255,0,255]
ui_font_caption = pygame.font.Font("ode_to_idle_gaming.otf", 15)
ui_tl_size = [500, 150]
ui_alpha = [0,0,0,0]
ui_glyphs = {
    'a':pygame.image.load('img/button/z.png'),
    'b':pygame.image.load('img/button/x.png'),
    'x':pygame.image.load('img/button/c.png'),
    'y':pygame.image.load('img/button/v.png')
    }

sfx_blip = pygame.mixer.Sound('sfx/blip.ogg')
sfx_oops = pygame.mixer.Sound('sfx/oops.wav')
sfx_good = pygame.mixer.Sound('sfx/good.ogg')
