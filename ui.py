import pygame, math
import constants

screensize = constants.ui_screensize
colorkey = constants.ui_colorkey
font_caption = constants.ui_font_caption
font_praise = constants.ui_font_praise
tl_size = constants.ui_tl_size
alpha = constants.ui_alpha
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

    def update(self, surface, pos):
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
        surface.blit(self.surface, [self.pos[0] - self.surface.get_width()/2,
                                    self.pos[1] - self.surface.get_height()/2])
