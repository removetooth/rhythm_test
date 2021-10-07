import pygame, math, time, sys, json
from glob import glob
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
    def __init__(self, button, start_time, pos, ghost = False):
        self.image = glyphs[button]
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
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                [i.on_click() for i in self.buttons]

    def draw(self, screen):
        interp = 1-min(1, (time.time()-self.paused_at)/0.15)
        self.bg.blit(self.bg_image, [-(time.time()*50%screensize[0]),0])
        self.bg.blit(self.bg_image, [-(time.time()*50%screensize[0])+screensize[0],0])
        pygame.draw.polygon(self.bg, colorkey, [
            [0,screensize[1]+(screensize[1]/4)*interp],
            [0,screensize[1]/4-(screensize[1]/4)*interp],
            [screensize[0],0-(screensize[1]/4)*interp],
            [screensize[0],3*screensize[1]/4+(screensize[1]/4)*interp]
            ])
        screen.blit(self.gray, [0,0])
        screen.blit(self.bg, [0,0])
        screen.blit(self.header, [30-(screensize[0]/4)*interp,20])
        [i.draw(screen) for i in self.buttons]


class ChartSelectScreen:
    def __init__(self):
        self.songs = []
        for i in glob('levels/*'):
            try:
                meta_f = open(i+'/meta.json','r')
                meta = json.loads(meta_f.read())
                meta_f.close() # i could shorten a lot of this if i skipped this line
            except:
                meta = {}
            self.songs.append(
                {
                    'path': i,
                    'name': meta.get('name', 'Untitled Chart'),
                    'chart_author': meta.get('chart_author', 'Unknown Author'),
                    #'preview': pygame.mixer.Sound(i+'/music.mp3'),
                    'name_text_header': font_pauseheader.render(
                        meta.get('name', 'Untitled Chart'), 0, [255,255,255]),
                    'name_text': font_caption.render(
                        meta.get('name', 'Untitled Chart'), 0, [255,255,255]),
                    'chart_author_text': font_caption.render(
                        "By " + meta.get('chart_author', 'Unknown Author'), 0, [255,255,255])
                }
            )
            
        self.buttons = [
            UIButton(
                "start",
                [screensize[0]/2, screensize[1]-30],
                [100,30],
                print,
                ["???"]
            )
        ]
        self.index = 0
        self.last_scroll = 0
        self.direction = 1
        self.bg_image = pygame.transform.scale(pausebg, screensize)
        #self.songs[self.index]['preview'].play(fade_ms=500)

    def update(self, events):
        self.buttons[0].args = [self.songs[self.index]['path']]
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    #self.songs[self.index]['preview'].fadeout(500)
                    self.last_scroll = time.time() if self.index != len(self.songs)-1 else 0
                    self.index = (self.index + 1) % len(self.songs)
                    #self.songs[self.index]['preview'].play(fade_ms=500)
                    self.direction = 1
                if event.key == pygame.K_UP:
                    #self.songs[self.index]['preview'].fadeout(500)
                    self.last_scroll = time.time() if self.index != 0 else 0
                    self.index = (self.index - 1) % len(self.songs)
                    #self.songs[self.index]['preview'].play(fade_ms=500)
                    self.direction = -1
            if event.type == pygame.MOUSEMOTION:
                [i.on_mouse_move(event) for i in self.buttons]
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                [i.on_click() for i in self.buttons]

    def draw(self, screen):
        interp = max(0,(0.15-(time.time()-self.last_scroll))/0.15)
        scroll = 0
        song = self.songs[self.index]
        header = song['name_text_header']
        author = song['chart_author_text']
        screen.blit(self.bg_image, [-(time.time()*50%screensize[0]),0])
        screen.blit(self.bg_image, [-(time.time()*50%screensize[0])+screensize[0],0])
        for i in range(self.index-3,self.index+4):
            if 0 <= i < len(self.songs):
                song_temp = self.songs[i]
                x = 50
                if i == self.index:
                    x = 50+20*(1-interp)
                elif i == self.index - self.direction:
                    x = 50+20*interp
                textalpha = 122-(max(abs(i-self.index),1)-2)*122
                if i-self.index <= -1:
                    textalpha += 122*interp*self.direction
                elif i-self.index >= 1:
                    textalpha -= 122*interp*self.direction

                song_temp['name_text'].set_alpha(textalpha)
                screen.blit(
                    song_temp['name_text'] if i != self.index \
                    else font_caption.render(
                        song_temp['name'], 0,
                        [
                            122+int(122*math.sin(time.time())),
                            122+int(122*math.cos(time.time())),
                            122-int(122*math.sin(time.time()))
                        ]
                    ),
                    [x, 170+scroll+30*interp*self.direction]
                )                    
            scroll += 30
        screen.blit(header, [30,20])
        screen.blit(author, [40, 20+header.get_height()])
        [i.draw(screen) for i in self.buttons]

    
