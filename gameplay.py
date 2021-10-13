from glob import glob
from os.path import basename, splitext
import math, json, time
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import misc, ui
from constants import *

class GameManager: # standard gameplay
    
    def __init__(self, chart):
        path = chart + "/"
        pygame.mixer.music.load(path + "music.mp3")
        with open(path + "chart.json") as f:
            self.song = json.loads(f.read())
            f.close()

        self.sounds = {splitext(basename(i))[0]: pygame.mixer.Sound(i) for i in glob(path + "sfx/*")}
        self.captions = [ui.font_caption.render(i['text'],0,[255,255,255]) for i in self.song['bars']]
        
        self.tl_dots_surf = pygame.Surface(ui.tl_size, pygame.SRCALPHA)
        self.tl_dots_surf.fill(ui.alpha)
        self.tl_beats_surf = pygame.Surface(ui.tl_size, pygame.SRCALPHA)
        self.tl_beats_surf.fill(ui.alpha)
        self.tl_beats = []

        self.praise = [PRAISE_PERFECT,-0.4]

        self.icons_pos = [0,0]
        self.icons_enabled = [False,False]
        self.icons_length = [0,0]

        self.events = []
        self.no_presses = [None, 0]
        self.next_input = [0,0]
        self.next_ghost_input = [0,0]

        self.interval = 60 / self.song['bpm']
        self.pulsed = 0
        self.beat = 0
        self.pos = 0
        self.bar_no = 0
        self.bar = self.song['bars'][self.bar_no]
        self.bar_beat = 0
        self.last_beat = 0
        self.last_bar_change = 0

        self.paused = False
        self.pauseScreen = ui.PauseScreen()
        self.pauseScreen.buttonMenu.setButtonFunc('resume', self.unpause)

        pygame.mixer.music.play()

    def update(self, events):
        self.events = events
        for event in events:
            if event.type == pygame.KEYDOWN and \
            event.key == pygame.K_ESCAPE:
                if not self.paused:
                    self.paused = True
                    self.pauseScreen.paused_at = time.time()
                    pygame.mixer.stop()
                    pygame.mixer.music.pause()
                    misc.sfx_pause.play()
                else:
                    self.unpause()
                    
        if self.paused:
            self.pauseScreen.update(events)
            return
        
        self.pos = pygame.mixer.music.get_pos() / 1000 - self.song['offset']
        self.beat = self.pos / self.interval
        if self.beat - self.last_beat > 0.5: # prevent unpause jank
            return
        self.last_beat = self.beat
        self.bar_beat = self.beat - self.last_bar_change
        [i.update(self.pos) for i in self.tl_beats]

        bar_handlers.get(self.bar['type'], GameManager.bar_break)(self, self.bar, self.bar_beat)
        if self.bar_no + 1 < len(self.song['bars']) and self.bar_beat >= self.bar['length'] - GAME_PREP_TIME:
            next_bar = self.song['bars'][self.bar_no+1]
            bar_prep_handlers.get(next_bar['type'], GameManager.bar_break_prep)(self, next_bar, self.bar_beat - self.bar['length'])

        if self.pos % self.interval < self.interval / 4 and not self.pulsed: # at beginning of beat
            self.pulsed = 1
            #misc.sfx_blip.play()
            if int(self.beat) - self.last_bar_change + 1 > self.bar['length']:
                GameManager.start_new_bar(self)
        elif self.pos % self.interval > self.interval - self.interval / 2 and \
             self.pos % self.interval < self.interval - self.interval / 4 and self.pulsed: # just before next beat
           self.pulsed = 0

        pass

    def draw(self, screen): # this is giving me a massive headache. i am so, so sorry
        screen.fill(ui.alpha)#[100,100,100,0])
        self.tl_beats_surf.fill(ui.alpha)
        pygame.draw.circle(screen,(255,255,255), [
            int(screen.get_width()*.25) + (self.pos/4%self.interval) * int(screen.get_width()*.50)/self.interval,
            int(screen.get_height()*.95) - 50*abs(math.sin(math.pi/self.interval*self.pos))
            ], 5)
        caption = self.captions[self.bar_no] if self.bar_no < len(self.song['bars']) \
                    else pygame.Surface([0,0])
        screen.blit(caption,
                    [int(screen.get_width()/2 - caption.get_width()/2),
                     int(screen.get_height()*.70)])
        screen.blit(self.tl_dots_surf,[screen.get_width()/2-self.tl_dots_surf.get_width()/2,25])
        [i.draw(self.tl_beats_surf) for i in self.tl_beats]
        if self.icons_enabled[0]:
            pygame.draw.circle(self.tl_beats_surf, [255,122,122],
                               ui.get_pos_on_tl(self.tl_beats_surf,self.icons_length[0],self.icons_pos[0],0),
                               10)
        if self.icons_enabled[1]:
            pygame.draw.circle(self.tl_beats_surf, [122,122,255],
                               ui.get_pos_on_tl(self.tl_beats_surf,self.icons_length[1],self.icons_pos[1],1),
                               10)
        screen.blit(self.tl_beats_surf,[screen.get_width()/2-self.tl_beats_surf.get_width()/2,25])

        if self.pos - self.praise[1] < 0.3:
            praise_surf = ui.praise[self.praise[0]]
            screen.blit(praise_surf, [
                screen.get_width()/2 - praise_surf.get_width()/2,
                30 + ui.tl_size[1] - 10*(self.pos-self.praise[1])/0.3
                ])

        if self.paused:
            self.pauseScreen.draw(screen)

    def drawGL(self):
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (ui.screensize[0]/ui.screensize[1]), 0.1, 50.0)
        glTranslatef(0.0,0.0, -5)
        glMatrixMode(GL_MODELVIEW)
        glRotatef(80*self.last_beat*self.interval,3,1,1)
        glColor3f(1,1,1)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()

    def drawOverGL(self):
        pass

    def unpause(self):
        pygame.mixer.music.unpause()
        self.paused = False

    def handle_input(self, bar, player = 1, pre = False): # yes, this is awful. i'll try to iterate on it
        for event in self.events:
            if event.type == pygame.KEYDOWN and event.key in misc.buttons:
                barpos = self.bar_beat - bar['length']*pre
                button = misc.buttons[event.key]
                if button in bar['sfx']:
                    if self.no_presses[0] == button:
                        self.no_presses[1] = (self.no_presses[1] + 1) % len(bar['sfx'][button])
                    else:
                        self.no_presses = [button, 0]
                    self.sounds[bar['sfx'][misc.buttons[event.key]][self.no_presses[1]]].play()
                    self.praise[0] = PRAISE_MISS
                    target_input = None
                    for i in bar['inputs']: # iterate on / figure out a better, cleaner implementation for this
                        if abs(barpos - i['beat']) < 1/32 and self.praise[0] < PRAISE_PERFECT:
                            self.praise[0] = PRAISE_PERFECT
                            target_input = i['button']
                        elif abs(barpos - i['beat']) < 1/16 and self.praise[0] < PRAISE_GREAT:
                            self.praise[0] = PRAISE_GREAT
                            target_input = i['button']
                        elif abs(barpos - i['beat']) < 1/8 and self.praise[0] < PRAISE_GOOD:
                            self.praise[0] = PRAISE_GOOD
                            target_input = i['button']
                        elif abs(barpos - i['beat']) < 1/4 and self.praise[0] < PRAISE_OK:
                            self.praise[0] = PRAISE_OK
                            target_input = i['button']
                    if button != target_input and self.praise[0] != PRAISE_MISS:
                        self.praise[0] = PRAISE_MISINPUT
                else:
                    misc.sfx_oops.play()
                    self.praise[0] = PRAISE_OOPS
                self.praise[1] = self.pos
                self.tl_beats.append(ui.HUDBeat(
                    button,
                    self.pos,
                    ui.get_pos_on_tl(self.tl_dots_surf, bar['length'], barpos, player)
                    ))
                        

    # ==== bar handling ====

    def start_new_bar(self):
        self.last_bar_change = int(self.beat)
        self.bar_no += 1
        next_bar = self.song['bars'][self.bar_no] if self.bar_no < len(self.song['bars']) \
                   else {'text':'','type':'break','length':1}
        next_next_bar = self.song['bars'][self.bar_no+1] if self.bar_no+1 < len(self.song['bars']) \
                   else {'text':'','type':'break','length':1}
        if self.bar['type'] == 'call':    # holy shit this is the worst
            self.next_input[0] = 0
            self.icons_enabled[0] = False
        elif self.bar['type'] == 'response':
            misc.sfx_good.play()
            self.tl_beats = []
            self.next_input[1] = 0
            self.icons_enabled[1] = False

        # TODO: figure out a COMPETENT way to draw the dots
        if next_bar['type'] == 'call':
            self.next_ghost_input[0] = 0
            ui.draw_dots(self.tl_dots_surf, next_bar['length'], 0)
            ui.draw_dots(self.tl_dots_surf, next_next_bar['length'], 1)
        elif next_bar['type'] == 'response':
            self.next_ghost_input[1] = 0
            ui.draw_dots(self.tl_dots_surf, next_bar['length'], 1)

        if next_bar['type'] == 'break':
            self.tl_dots_surf.fill(ui.alpha)
            

        self.bar = next_bar
        
        pass

    def bar_call(self, bar, beat):
        self.icons_enabled[0] = True
        self.icons_length[0] = bar['length']
        self.icons_pos[0] = beat
        if self.next_input[0] < len(bar['inputs']):
            target = bar['inputs'][self.next_input[0]]
            if self.bar_beat >= target['beat']:
                self.sounds[target['sound']].play()
                self.tl_beats.append(ui.HUDBeat(
                    target['button'],
                    self.pos,
                    ui.get_pos_on_tl(self.tl_dots_surf,bar['length'],target['beat'],0)
                    ))
                self.next_input[0] += 1
        pass

    def bar_call_prep(self, bar, beat):
        self.icons_enabled[0] = True
        self.icons_length[0] = bar['length']
        self.icons_pos[0] = beat
        prog = bar['length'] * (GAME_PREP_TIME - beat) / GAME_PREP_TIME
        #if self.next_ghost_input[0] < len(bar['inputs']):
        #    target = bar['inputs'][self.next_ghost_input[0]]
        #    if prog >= target['beat']:
        #        self.tl_beats.append(ui.HUDBeat(
        #            target['button'],
        #            self.pos,
        #            ui.get_pos_on_tl(self.tl_dots_surf,bar['length'],target['beat'],0),
        #            ghost = True
        #            ))
        #        self.next_ghost_input[0] += 1    # doesn't work right and i'm too tired to fix it.
        pass

    def bar_response(self, bar, beat):
        self.icons_enabled[1] = True
        self.icons_length[1] = bar['length']
        self.icons_pos[1] = beat
        GameManager.handle_input(self, bar)
        pass

    def bar_response_prep(self, bar, beat):
        self.icons_enabled[1] = True
        self.icons_length[1] = bar['length']
        self.icons_pos[1] = beat
        GameManager.handle_input(self, bar, pre=1)
        prog = bar['length'] * (GAME_PREP_TIME + beat) / GAME_PREP_TIME
        if self.next_ghost_input[1] < len(bar['inputs']):
            target = bar['inputs'][self.next_ghost_input[1]]
            if prog >= target['beat']:
                self.tl_beats.append(ui.HUDBeat(
                    target['button'],
                    self.pos,
                    ui.get_pos_on_tl(self.tl_dots_surf,bar['length'],target['beat'],1),
                    ghost = True
                    ))
                self.next_ghost_input[1] += 1
        pass

    def bar_simultaneous(self, bar, beat):
        pass

    def bar_simultaneous_prep(self, bar, beat):
        pass

    def bar_break(self, bar, beat):
        pass

    def bar_break_prep(self, bar, beat):
        pass

bar_handlers = {
    "call": GameManager.bar_call,
    "response": GameManager.bar_response,
    "simultaneous": GameManager.bar_simultaneous,
    "break": GameManager.bar_break
    }
bar_prep_handlers = {
    "call": GameManager.bar_call_prep,
    "response": GameManager.bar_response_prep,
    "simultaneous": GameManager.bar_simultaneous_prep,
    "break": GameManager.bar_break_prep
    }

def score():
    # scoring system, i'll work on it in a bit
    return 0

vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )
