from glob import glob
from os.path import basename, splitext
import math, json
import pygame
import constants, ui

class GameManager: # standard gameplay
    
    def __init__(self, chart):
        path = "levels/" + chart + "/"
        print("Loading song...")
        with open(path + "/chart.json") as f:
            self.song = json.loads(f.read())
            f.close()

        self.sounds = {splitext(basename(i))[0]: pygame.mixer.Sound(i) for i in glob(path + "sfx/*")}
        self.captions = [ui.font_caption.render(i['text'],0,[255,255,255]) for i in self.song['bars']]
        
        self.tl_dots_surf = pygame.Surface(ui.tl_size)
        self.tl_dots_surf.set_colorkey(ui.colorkey)
        self.tl_dots_surf.fill(ui.colorkey)
        self.tl_beats_surf = pygame.Surface(ui.tl_size, pygame.SRCALPHA)
        self.tl_beats_surf.fill(ui.alpha)
        self.tl_beats = []

        self.praise = [0,-0.3]

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

    def update(self, t, events):
        self.events = events
        self.pos = t / 1000 - self.song['offset']
        self.beat = self.pos / self.interval
        if self.beat - self.last_beat > 0.25: # prevent unpause jank
            return
        self.last_beat = self.beat
        self.bar_beat = self.beat - self.last_bar_change
        [i.update(self.pos) for i in self.tl_beats]

        bar_handlers.get(self.bar['type'], GameManager.bar_break)(self, self.bar, self.bar_beat)
        if self.bar_no + 1 < len(self.song['bars']) and self.bar_beat >= self.bar['length'] - constants.prep_time:
            next_bar = self.song['bars'][self.bar_no+1]
            bar_prep_handlers.get(next_bar['type'], GameManager.bar_break_prep)(self, next_bar, self.bar_beat - self.bar['length'])

        if self.pos % self.interval < self.interval / 4 and not self.pulsed: # at beginning of beat
            self.pulsed = 1
            #constants.sfx_blip.play()
            if int(self.beat) - self.last_bar_change + 1 > self.bar['length']:
                GameManager.start_new_bar(self)
        elif self.pos % self.interval > self.interval - self.interval / 2 and \
             self.pos % self.interval < self.interval - self.interval / 4 and self.pulsed: # just before next beat
           self.pulsed = 0

        pass

    def draw(self, screen): # this is giving me a massive headache. i am so, so sorry
        screen.fill([100,100,100])
        self.tl_beats_surf.fill(ui.alpha)
        pygame.draw.circle(screen,(255,255,255), [
            int(screen.get_width()*.25) + (self.pos/4%self.interval) * int(screen.get_width()*.50)/self.interval,
            int(screen.get_height()*.95) - 50*abs(math.sin(math.pi/self.interval*self.pos))
            ], 5)
        screen.blit(self.captions[self.bar_no],
                    [int(screen.get_width()/2 - self.captions[self.bar_no].get_width()/2),
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

    def handle_input(self, bar, player = 1, pre = False): # yes, this is awful. i'll try to iterate on it
        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key in constants.buttons:
                    barpos = self.bar_beat - bar['length']*pre
                    button = constants.buttons[event.key]
                    if button in bar['sfx']:
                        if self.no_presses[0] == button:
                            self.no_presses[1] = (self.no_presses[1] + 1) % len(bar['sfx'][button])
                        else:
                            self.no_presses = [button, 0]
                        self.sounds[bar['sfx'][constants.buttons[event.key]][self.no_presses[1]]].play()
                        highest_praise = 0
                        target_input = None
                        for i in bar['inputs']: # iterate on / figure out a better, cleaner implementation for this
                            if abs(barpos - i['beat']) < 1/32 and highest_praise < 4:
                                self.praise[0] = 0
                                highest_praise = 4
                                target_input = i['button']
                            elif abs(barpos - i['beat']) < 1/16 and highest_praise < 3:
                                self.praise[0] = 1
                                highest_praise = 3
                                target_input = i['button']
                            elif abs(barpos - i['beat']) < 1/8 and highest_praise < 2:
                                self.praise[0] = 2
                                highest_praise = 2
                                target_input = i['button']
                            elif abs(barpos - i['beat']) < 1/4 and highest_praise < 1:
                                self.praise[0] = 3
                                highest_praise = 1
                                target_input = i['button']
                        if button != target_input:
                            self.praise[0] = 6
                        if highest_praise == 0:
                            self.praise[0] = 4
                    else:
                        constants.sfx_oops.play()
                        self.praise[0] = 5
                    self.praise[1] = self.pos
                    self.tl_beats.append(ui.HUDBeat(
                        ui.glyphs[button],
                        self.pos,
                        ui.get_pos_on_tl(self.tl_dots_surf, bar['length'], barpos, player)
                        ))
                        

    # ==== bar handling ====

    def start_new_bar(self):
        self.last_bar_change = int(self.beat)
        next_bar = self.song['bars'][self.bar_no+1]
        if self.bar['type'] == 'call':    # holy shit this is the worst
            self.next_input[0] = 0
            self.icons_enabled[0] = False
        elif self.bar['type'] == 'response':
            constants.sfx_good.play()
            self.tl_beats = []
            self.next_input[1] = 0
            self.icons_enabled[1] = False

        if next_bar['type'] == 'call':
            self.next_ghost_input[0] = 0
        elif next_bar['type'] == 'response':
            self.next_ghost_input[1] = 0

        self.bar_no += 1
        self.bar = self.song['bars'][self.bar_no]
        ui.draw_dots(self.tl_dots_surf, self.bar['length'])
        
        pass

    def bar_call(self, bar, beat):
        self.icons_enabled[0] = True
        self.icons_length[0] = bar['length']
        self.icons_pos[0] = beat
        if self.next_input[0] < len(bar['inputs']):
            target = bar['inputs'][self.next_input[0]]
            if self.bar_beat >= target['beat']:
                self.sounds[target['sound']].play()
                self.tl_beats.append(ui.HUDBeat(ui.glyphs[target['button']],
                                         self.pos,
                                         ui.get_pos_on_tl(self.tl_dots_surf,bar['length'],target['beat'],0)
                                         )
                                 )
                self.next_input[0] += 1
        pass

    def bar_call_prep(self, bar, beat):
        self.icons_enabled[0] = True
        self.icons_length[0] = bar['length']
        self.icons_pos[0] = beat
        prog = bar['length'] * (constants.prep_time - beat) / constants.prep_time
        #if self.next_ghost_input[0] < len(bar['inputs']):
        #    target = bar['inputs'][self.next_ghost_input[0]]
        #    if prog >= target['beat']:
        #        self.tl_beats.append(ui.HUDBeat(
        #            ui.glyphs[target['button']],
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
        prog = bar['length'] * (constants.prep_time + beat) / constants.prep_time
        if self.next_ghost_input[1] < len(bar['inputs']):
            target = bar['inputs'][self.next_ghost_input[1]]
            if prog >= target['beat']:
                self.tl_beats.append(ui.HUDBeat(
                    ui.glyphs[target['button']],
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
