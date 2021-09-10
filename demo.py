from glob import glob
from os.path import basename, splitext
import time
import math
import json 

import pygame
pygame.init()

import constants

pygame.mixer.init()
screen = pygame.display.set_mode(constants.ui_screensize)

chart_folder = "levels/test/" # temp


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
                                          [int(math.fabs(math.cos(t*9*(1-self.transparent))*self.surface.get_width()/2))+extra,
                                           int(self.surface.get_height()/2)+extra])
            self.surface.fill(constants.ui_colorkey)
            self.surface.blit(temp, [self.surface.get_width()/2 - temp.get_width()/2,
                                     self.surface.get_height()/2 - temp.get_height()/2])
        surface.blit(self.surface, [self.pos[0] - self.surface.get_width()/2,
                                    self.pos[1] - self.surface.get_height()/2])


bar_surf = pygame.Surface(constants.ui_tl_size)
bar_surf.set_colorkey(constants.ui_colorkey)
bar_surf.fill(constants.ui_colorkey)
beats_surf = pygame.Surface(constants.ui_tl_size, pygame.SRCALPHA)
beats_surf.fill(constants.ui_alpha)
clock = pygame.time.Clock()
    
print('Loading song...')
with open(chart_folder + "chart.json") as f:
    song = json.loads(f.read())
    f.close()
    
sounds = {splitext(basename(i))[0]: i for i in glob(chart_folder + "sfx/*")}
for i in sounds:
    print("SFX:", i, sounds[i])
    temp = pygame.mixer.Sound(sounds[i])
    sounds[i] = temp
    
captions = []
for i in song['bars']:
    print("Rendering caption:", i['text'])
    captions.append(constants.ui_font_caption.render(i['text'],0,(255,255,255)))

interval = 60 / song['bpm']
pygame.mixer.music.load(chart_folder + 'music.mp3')
pygame.mixer.music.play()

# all of this should go into a game manager object later on
pulsed = 0
bar_no = 0
bar = song['bars'][bar_no]
draw_dots(bar_surf, bar['length'])
bar_timestamp = 0
next_input = 0
no_presses = [None, 0]
bar_beat_discrete = 0
beats_so_far = 0
hud_beats = []

while pygame.mixer.music.get_busy():
    clock.tick()
    events = pygame.event.get()
            
    pos = pygame.mixer.music.get_pos() / 1000 - song['offset']
    beat = pos/interval
    bar_beat = (pos-bar_timestamp)/interval
    #pygame.display.set_caption(str(clock.get_fps()))
    
    screen.fill([100,100,100])
    beats_surf.fill(constants.ui_alpha)
    
    if bar['type'] == 'call':

        screen.blit(bar_surf,[screen.get_width()/2-bar_surf.get_width()/2,25])
        screen.blit(captions[bar_no],[int(screen.get_width()/2 - captions[bar_no].get_width()/2),int(screen.get_height()*.70)])
        pygame.draw.circle(beats_surf, [255,122,122],
                           get_pos_on_tl(beats_surf,bar['length'],bar_beat,0),
                           10)

        if next_input < len(bar['inputs']):
            target = bar['inputs'][next_input]
            if bar_beat >= target['beat']:
                sounds[target['sound']].play() # i've got to make this cleaner
                hud_beats.append(HUDBeat(constants.ui_glyphs[target['button']],
                                         pos,
                                         get_pos_on_tl(bar_surf,bar['length'],target['beat'],0)
                                         )
                                 )
                hud_beats.append(HUDBeat(constants.ui_glyphs[target['button']], # bad implementation, handle properly later
                                         pos,
                                         get_pos_on_tl(bar_surf,bar['length'],target['beat'],1),
                                         ghost = True
                                         )
                                 )
                next_input += 1

        if bar_beat >= bar['length']-1 and bar_no + 1 < len(song['bars']):
            pygame.draw.circle(beats_surf, [122,122,255],
                           get_pos_on_tl(beats_surf,bar['length'],bar_beat-bar['length'],1),
                           10)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in constants.buttons:
                        if constants.buttons[event.key] in song['bars'][bar_no+1]['sfx']:
                            if no_presses[0] == constants.buttons[event.key]:      # WHY DID I PASTE THIS A SECOND DAMN TIME THERE HAS GOT TO BE A BETTER WAY TO DO THIS
                                if no_presses[1] < len(song['bars'][bar_no+1]['sfx'][constants.buttons[event.key]])-1:
                                    no_presses[1] += 1
                                else:
                                    no_presses[1] = 0
                            else:
                                no_presses = [constants.buttons[event.key], 0]
                            sounds[song['bars'][bar_no+1]['sfx'][constants.buttons[event.key]][no_presses[1]]].play()
                        else:
                            constants.sfx_oops.play()
                        hud_beats.append(HUDBeat(constants.ui_glyphs[constants.buttons[event.key]],
                                             pos,
                                             get_pos_on_tl(bar_surf,bar['length'],bar_beat-bar['length'],1)
                                             )
                                         )
            

    elif bar['type'] == 'response':
        
        screen.blit(bar_surf,[screen.get_width()/2-bar_surf.get_width()/2,25])
        screen.blit(captions[bar_no],[int(screen.get_width()/2 - captions[bar_no].get_width()/2),int(screen.get_height()*.70)])
        pygame.draw.circle(beats_surf, [122,122,255],
                           get_pos_on_tl(beats_surf,bar['length'],bar_beat,1),
                           10)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in constants.buttons:
                    if constants.buttons[event.key] in bar['sfx']:
                        if no_presses[0] == constants.buttons[event.key]:      # THIS IS AWFUL OH MY GOD
                            if no_presses[1] < len(bar['sfx'][constants.buttons[event.key]])-1:
                                no_presses[1] += 1
                            else:
                                no_presses[1] = 0
                        else:
                            no_presses = [constants.buttons[event.key], 0]
                        sounds[bar['sfx'][constants.buttons[event.key]][no_presses[1]]].play()
                    else:
                        constants.sfx_oops.play()
                    hud_beats.append(HUDBeat(constants.ui_glyphs[constants.buttons[event.key]],
                                         pos,
                                         get_pos_on_tl(bar_surf,bar['length'],bar_beat,1)
                                         )
                                     )
                
    pygame.draw.circle(screen,(255,255,255), [
        int(screen.get_width()*.25) + (pos/4%interval) * int(screen.get_width()*.50)/interval,
        int(screen.get_height()*.95) - 50*math.fabs(math.sin(math.pi/interval*pos))
        ], 5)
    [i.update(beats_surf, pos) for i in hud_beats]
    screen.blit(beats_surf,[screen.get_width()/2-beats_surf.get_width()/2,25])
    
    pygame.display.flip()
    if pos % interval < interval / 4 and not pulsed:
        pulsed = 1
        constants.sfx_blip.play()
        bar_beat_discrete = int(beat) - beats_so_far
        if bar_beat_discrete+1 > bar['length']: # start a new bar
            if bar['type'] == 'response':
                constants.sfx_good.play()
                hud_beats = []
            bar_no += 1
            beats_so_far += bar['length']
            bar = song['bars'][bar_no]
            bar_timestamp = pos
            next_input = 0
            draw_dots(bar_surf, bar['length'])
            
    elif pos % interval > interval - interval / 2 and pos % interval < interval - interval / 4 and pulsed:
        pulsed = 0
