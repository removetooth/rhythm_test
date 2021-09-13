import pygame, math, time, sys
import constants

screensize = constants.ui_screensize
colorkey = constants.ui_colorkey
font_caption = constants.ui_font_caption
font_praise = constants.ui_font_praise
font_button = constants.ui_font_button
font_pauseheader = constants.ui_font_pauseheader
tl_size = constants.ui_tl_size
alpha = constants.ui_alpha
pausebg = constants.ui_pausebg
glyphs = constants.ui_glyphs
praise = constants.ui_praise

def get_pos_on_tl(surface, length, beat, player):
    # used to find the graphical position on the timeline,
    # based on t, length of bar, and size of surface
    if length <= 4:
        y = surface.get_height()/4
    else:
        y = surface.get_height()/6 * (int(beat*4/16)+1)
    if beat >= 0:
        x = (surface.get_width()/17) * (beat*4%16 + 1)
    else:
        x = (surface.get_width()/17) * (beat*4 + 1)
    y += surface.get_height() / 2 * player
    return [int(x), int(y)]

def draw_dots(surface, length):
    # used for the timeline at the top
    length = int(length * 4)
    surface.fill(constants.ui_colorkey)
    for i in range(length):
        radius = 4
        if i % 4 == 0:
            radius = 7
        pygame.draw.circle(surface, [255,255,255], get_pos_on_tl(surface,length/4,i/4,0),radius)
        pygame.draw.circle(surface, [255,255,255], get_pos_on_tl(surface,length/4,i/4,1),radius)
    
class HUDBeat:
    def __init__(self, image, start_time, pos, ghost = False):
        self.image = image
        self.start_time = start_time
        self.pos = pos
        self.transparent = ghost
        self.surface = pygame.Surface([[50,50], [40,40]][ghost])
        self.surface.set_colorkey(constants.ui_colorkey)
        self.surface.set_alpha([255, 0][ghost])
        self.surface.fill(constants.ui_colorkey)

    def update(self, pos):
        t = pos - self.start_time
        extra = 0
        if t < 0.25:
            extra = int(15 * (0.25 - t)/0.25)
            if self.transparent:
                self.surface.set_alpha(200*t/0.25)
        if t*9 <= math.pi*2:
            temp = pygame.transform.scale(self.image,
                                          [int(abs(math.cos(t*9*(1-self.transparent))*self.surface.get_width()/2))+extra,
                                           int(self.surface.get_height()/2)+extra])
            self.surface.fill(constants.ui_colorkey)
            self.surface.blit(temp, [self.surface.get_width()/2 - temp.get_width()/2,
                                     self.surface.get_height()/2 - temp.get_height()/2])
        
    def draw(self, surface):
        surface.blit(self.surface, [self.pos[0] - self.surface.get_width()/2,
                                    self.pos[1] - self.surface.get_height()/2])

class UIButton:
    def __init__(self, text, pos, size, func_onclick, args = []):
        self.size = size
        self.center = pos
        self.corner = [
            int(self.center[0] - self.size[0] / 2),
            int(self.center[1] - self.size[1] / 2)
            ]
        self.text = text
        self.text_surf = font_button.render(self.text,0,[255,255,255])
        self.func_onclick = func_onclick
        self.args = args
        self.last_interaction = 0
        self.moused = False
        self.surface = pygame.Surface(size, pygame.SRCALPHA)

    def on_click(self):
        if self.moused:
            self.func_onclick(*self.args)

    def on_mouse_move(self, event):
        if event.pos[0] in range(self.corner[0], self.corner[0]+self.size[0]+1) and \
           event.pos[1] in range(self.corner[1], self.corner[1]+self.size[1]+1) and \
           not self.moused:
            self.moused = True
            self.last_interaction = time.time()
        elif (not event.pos[0] in range(self.corner[0], self.corner[0]+self.size[0]+1) or \
             not event.pos[1] in range(self.corner[1], self.corner[1]+self.size[1]+1)) and \
             self.moused:
            self.moused = False
            self.last_interaction = time.time()

    def draw(self, screen):
        self.surface.fill(alpha)
        if self.moused:
            interp = min(1,(time.time()-self.last_interaction)/0.1)
        else:
            interp = max(0,(0.1-(time.time()-self.last_interaction))/0.1)
        pygame.draw.rect(self.surface, [0,0,0,100 + 50*interp],
                         [self.size[0]/20*(1-interp), 0,
                          self.size[0]-self.size[0]/10*(1-interp),
                          self.size[1]]
                         )
        self.surface.blit(self.text_surf, [
            self.size[0]/2 - self.text_surf.get_width() / 2,
            self.size[1]/2 - self.text_surf.get_height() / 2
            ])
        screen.blit(self.surface, self.corner)

class PauseScreen:
    def __init__(self):
        self.buttons = [ # placeholder for now
            UIButton("resume", [screensize[0]/2, screensize[1]/2-30], [100,30], pygame.mixer.music.unpause),
            UIButton("quit", [screensize[0]/2, screensize[1]/2+30], [100,30], sys.exit),
            ]
        self.gray = pygame.Surface(screensize)
        self.gray.fill([0,0,0])
        self.gray.set_alpha(100)
        self.bg = pygame.Surface(screensize)
        self.bg.set_colorkey(colorkey)
        self.bg.fill([0,0,0])
        self.bg_image = pygame.transform.scale(pausebg, screensize)
        self.paused_at = 0
        self.header = font_pauseheader.render("Paused", 0, [255,255,255])

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                [i.on_mouse_move(event) for i in self.buttons]
            elif event.type == pygame.MOUSEBUTTONUP:
                [i.on_click() for i in self.buttons]

    def draw(self, screen):
        interp = 0#1-min(1, (time.time()-self.paused_at)/0.15)
        self.bg.blit(self.bg_image, [-(time.time()*50%screensize[0]),0])
        self.bg.blit(self.bg_image, [-(time.time()*50%screensize[0])+screensize[0],0])
        pygame.draw.polygon(self.bg, colorkey, [
            [0-(screensize[0]/4)*interp,screensize[1]],
            [screensize[0]/4-(screensize[0]/4)*interp,0],
            [screensize[0]+(screensize[0]/4)*interp,0],
            [3*screensize[0]/4+(screensize[0]/4)*interp,screensize[1]]
            ])
        screen.blit(self.gray, [0,0])
        screen.blit(self.bg, [0,0])
        screen.blit(self.header, [30,20])
        [i.draw(screen) for i in self.buttons]

    
