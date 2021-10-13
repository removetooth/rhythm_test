import pygame, math, time, sys, json
from OpenGL.GL import *
from glob import glob
import misc
from constants import *

screensize = [640,480]#[1280,720]
font_caption = pygame.font.Font("ode_to_idle_gaming.otf", 15)
font_praise = pygame.font.Font("ode_to_idle_gaming.otf", 15)
font_button = pygame.font.Font("ode_to_idle_gaming.otf", 14)
font_pauseheader = pygame.font.Font("ode_to_idle_gaming.otf", 35)
tl_size = [500, 150]
alpha = [0,0,0,0]
pausebg = pygame.image.load('img/ui/pause_bg.png')
glyphs = {
    'a':pygame.image.load('img/button/x.png'),
    'b':pygame.image.load('img/button/c.png'),
    'x':pygame.image.load('img/button/z.png'),
    'y':pygame.image.load('img/button/s.png'),
    'l':pygame.image.load('img/button/a.png'),
    'r':pygame.image.load('img/button/d.png'),
    'up':pygame.image.load('img/button/kb_up.png'),
    'down':pygame.image.load('img/button/kb_down.png'),
    'left':pygame.image.load('img/button/kb_left.png'),
    'right':pygame.image.load('img/button/kb_right.png'),
    }
praise = {
    PRAISE_PERFECT:font_praise.render('perfect!', 0, [200,200,0]),
    PRAISE_GREAT:font_praise.render('great!', 0, [0,255,0]),
    PRAISE_GOOD:font_praise.render('good', 0, [200,200,255]),
    PRAISE_OK:font_praise.render('eh...', 0, [0,0,200]),
    PRAISE_MISS:font_praise.render('miss', 0, [200,0,0]),
    PRAISE_OOPS:font_praise.render('oops!', 0, [200,0,0]),
    PRAISE_MISINPUT:font_praise.render('wrong button', 0, [200,100,0])
    }

surface = pygame.Surface(screensize, pygame.SRCALPHA)

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
    surface.fill(alpha)
    for i in range(length):
        radius = 4
        if i % 4 == 0:
            radius = 7
        pygame.draw.circle(surface, [255,255,255], get_pos_on_tl(surface,length/4,i/4,0),radius)
        pygame.draw.circle(surface, [255,255,255], get_pos_on_tl(surface,length/4,i/4,1),radius)

def surfaceToTexture( pygame_surface, texture ):
    rgb_surface = pygame.image.tostring( pygame_surface, 'RGBA')
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    surface_rect = pygame_surface.get_rect()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface_rect.width, surface_rect.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, rgb_surface)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)
  
class HUDBeat:
    def __init__(self, button, start_time, pos, ghost = False):
        self.image = glyphs[button]
        self.start_time = start_time
        self.pos = pos
        self.transparent = ghost
        self.surface = pygame.Surface([[50,50], [40,40]][ghost]).convert_alpha(surface)
        self.surface.set_alpha([255, 0][ghost])
        self.surface.fill(alpha)

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
            self.surface.fill(alpha)
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
        self.surface = pygame.Surface(size).convert_alpha(surface)
        self.kbnav = [None,None,None,None]
        self.inhibit_next_kb_event = False

    def on_click(self, event):
        if self.moused and event.button == 1:
            self.func_onclick(*self.args)

    def on_mouse_move(self, event):
        if event.pos[0] in range(self.corner[0], self.corner[0]+self.size[0]+1) and \
           event.pos[1] in range(self.corner[1], self.corner[1]+self.size[1]+1) and \
           not self.moused:
            self.set_hl(1)
        elif (not event.pos[0] in range(self.corner[0], self.corner[0]+self.size[0]+1) or \
             not event.pos[1] in range(self.corner[1], self.corner[1]+self.size[1]+1)) and \
             self.moused:
            self.set_hl(0)

    def on_key_press(self, event):
        key = misc.buttons.get(event.key, None)
        if self.moused and not self.inhibit_next_kb_event:
            if key in ['up', 'down', 'left', 'right']:
                d = {'up':0, 'down':1, 'left':2, 'right':3}[misc.buttons[event.key]]
                if self.kbnav[d] != None:
                    self.set_hl(0)
                    self.kbnav[d].set_hl(1)
            elif key == 'a':
                self.func_onclick(*self.args)

    def draw(self, screen):
        self.inhibit_next_kb_event = False
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
        ts = self.text_surf if not self.moused \
             else font_button.render(self.text, 0,
                  [122+int(122*math.sin(time.time())),
                   122+int(122*math.cos(time.time())),
                   122-int(122*math.sin(time.time()))])
        self.surface.blit(ts, [
            self.size[0]/2 - self.text_surf.get_width() / 2,
            self.size[1]/2 - self.text_surf.get_height() / 2
            ])
        screen.blit(self.surface, self.corner)

    def set_hl(self, hl): # set highlight func for keyboard navigation
        self.moused = hl
        self.last_interaction = time.time()
        self.inhibit_next_kb_event = True

    def set_kbnav(self, direction, button):
        """
        void set_kbnav (direction, button)
        Sets the button to highlight when a direction key is pressed.
        0 - up, 1 - down, 2 - left, 3 - right
        """
        if type(button) in [UIButton, type(None)]:
            self.kbnav[direction] = button
        else:
            print("set_kbnav: button must be type UIButton or NoneType")

class PauseScreen:
    def __init__(self):
        self.buttons = [ # placeholder for now
            UIButton("resume", [screensize[0]/2, screensize[1]/2-30], [100,30], pygame.mixer.music.unpause),
            UIButton("quit", [screensize[0]/2, screensize[1]/2+30], [100,30], sys.exit),
            ]
        self.buttons[0].set_kbnav(1, self.buttons[1])
        self.buttons[1].set_kbnav(0, self.buttons[0])
        self.buttons[0].set_kbnav(0, self.buttons[1])
        self.buttons[1].set_kbnav(1, self.buttons[0])
        self.bg = pygame.Surface(screensize).convert_alpha(surface)
        self.bg.fill([0,0,0])
        self.bg_image = pygame.transform.scale(pausebg, screensize).convert_alpha(surface)
        self.paused_at = 0
        self.header = font_pauseheader.render("Paused", 0, [255,255,255])

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                [i.on_mouse_move(event) for i in self.buttons]
            elif event.type == pygame.MOUSEBUTTONUP:
                [i.on_click(event) for i in self.buttons]
            elif event.type == pygame.KEYDOWN:
                [i.on_key_press(event) for i in self.buttons]
                if len([i for i in self.buttons if i.moused]) == 0:
                    self.buttons[0].set_hl(1)

    def draw(self, screen):
        interp = 1-min(1, (time.time()-self.paused_at)/0.15)
        self.bg.blit(self.bg_image, [-(time.time()*50%screensize[0]),0])
        self.bg.blit(self.bg_image, [-(time.time()*50%screensize[0])+screensize[0],0])
        pygame.draw.polygon(self.bg, [0,0,0,100], [
            [0,screensize[1]+(screensize[1]/4)*interp],
            [0,screensize[1]/4-(screensize[1]/4)*interp],
            [screensize[0],0-(screensize[1]/4)*interp],
            [screensize[0],3*screensize[1]/4+(screensize[1]/4)*interp]
            ])
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
        self.buttons[0].set_hl(1)
        self.index = 0
        self.last_scroll = 0
        self.direction = 1
        self.bg_image = pygame.transform.scale(pausebg, screensize)
        #self.songs[self.index]['preview'].play(fade_ms=500)

    def update(self, events):
        self.buttons[0].args = [self.songs[self.index]['path']]
        for event in events:
            if event.type == pygame.KEYDOWN:
                key = misc.buttons.get(event.key, None)
                [i.on_key_press(event) for i in self.buttons]
                if len([i for i in self.buttons if i.moused]) == 0 and \
                   key in ['left', 'right']:
                    self.buttons[0].set_hl(1)
                if key == "down":
                    #self.songs[self.index]['preview'].fadeout(500)
                    self.last_scroll = time.time() if self.index != len(self.songs)-1 else 0
                    self.index = (self.index + 1) % len(self.songs)
                    #self.songs[self.index]['preview'].play(fade_ms=500)
                    self.direction = 1
                if key == "up":
                    #self.songs[self.index]['preview'].fadeout(500)
                    self.last_scroll = time.time() if self.index != 0 else 0
                    self.index = (self.index - 1) % len(self.songs)
                    #self.songs[self.index]['preview'].play(fade_ms=500)
                    self.direction = -1
            if event.type == pygame.MOUSEMOTION:
                [i.on_mouse_move(event) for i in self.buttons]
            elif event.type == pygame.MOUSEBUTTONUP:
                [i.on_click(event) for i in self.buttons]

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

    def drawGL(self):
        pass

    def drawOverGL(self):
        pass

    
