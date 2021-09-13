import pygame

chart = "test"

prep_time = 1
# this is fairly roundabout and can probably just be replaced with keycodes
buttons = {pygame.K_z:'a',pygame.K_x:'b',pygame.K_c:'x',pygame.K_v:'y',
           pygame.K_UP:'up',pygame.K_DOWN:'down',pygame.K_LEFT:'left',pygame.K_RIGHT:'right',
           pygame.K_w:'up',pygame.K_s:'down',pygame.K_a:'left',pygame.K_d:'right'}

ui_screensize = [640,480]
ui_colorkey = [255,0,255]
ui_font_caption = pygame.font.Font("ode_to_idle_gaming.otf", 15)
ui_font_praise = pygame.font.Font("ode_to_idle_gaming.otf", 15)
ui_font_button = pygame.font.Font("ode_to_idle_gaming.otf", 14)
ui_font_pauseheader = pygame.font.Font("ode_to_idle_gaming.otf", 35)
ui_tl_size = [500, 150]
ui_alpha = [0,0,0,0]
ui_pausebg = pygame.image.load('img/ui/pause_bg.png')
ui_glyphs = {
    'a':pygame.image.load('img/button/z.png'),
    'b':pygame.image.load('img/button/x.png'),
    'x':pygame.image.load('img/button/c.png'),
    'y':pygame.image.load('img/button/v.png'),
    'up':pygame.image.load('img/button/kb_up.png'),
    'down':pygame.image.load('img/button/kb_down.png'),
    'left':pygame.image.load('img/button/kb_left.png'),
    'right':pygame.image.load('img/button/kb_right.png'),
    }
ui_praise = [
    ui_font_praise.render('perfect!', 0, [200,200,0]),
    ui_font_praise.render('great!', 0, [0,255,0]),
    ui_font_praise.render('good', 0, [200,200,255]),
    ui_font_praise.render('eh...', 0, [0,0,200]),
    ui_font_praise.render('miss', 0, [200,0,0]),
    ui_font_praise.render('oops!', 0, [200,0,0]),
    ui_font_praise.render('wrong button', 0, [200,100,0])
    ]

sfx_blip = pygame.mixer.Sound('sfx/blip.ogg')
sfx_oops = pygame.mixer.Sound('sfx/oops.wav')
sfx_good = pygame.mixer.Sound('sfx/good.ogg')
sfx_pause = pygame.mixer.Sound('sfx/pause.ogg')
