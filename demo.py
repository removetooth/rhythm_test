import time
import math

import pygame

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([640,480])


song = {
    'song':'levels/test/sexer.mp3',
    'bpm':163,
    'offset':0.02,
    'sounds':{
        'stfu_shut': 'levels/test/sfx/stfu_shut.ogg',
        'stfu_the': 'levels/test/sfx/stfu_the.ogg',
        'stfu_fuck': 'levels/test/sfx/stfu_fuck.ogg',
        'stfu_up': 'levels/test/sfx/stfu_up.ogg',
        'pl_stfu_shut': 'levels/test/sfx/pl_stfu_shut.ogg',
        'pl_stfu_the': 'levels/test/sfx/pl_stfu_the.ogg',
        'pl_stfu_fuck': 'levels/test/sfx/pl_stfu_fuck.ogg',
        'pl_stfu_up': 'levels/test/sfx/pl_stfu_up.ogg'
    },
    'bars':[
        {
            'text':'',
            'type':'break',
            'length':8
        },
        {
            'text':'Shut the fuck up.',
            'type':'call',
            'length':4,
            'inputs':{
                0:{"button":"a","sound":"stfu_shut"},
                1:{"button":"b","sound":"stfu_the"},
                1.5:{"button":"x","sound":"stfu_fuck"},
                2.5:{"button":"x","sound":"stfu_up"}
            }
        },
        {
            'text':'Shut the fuck up!',
            'type':'response',
            'length':4,
            'sfx':{
                'a':['pl_stfu_shut'],
                'b':['pl_stfu_the'],
                'x':['pl_stfu_fuck','pl_stfu_up']
            },
            'inputs':{
                0:'a',
                1:'b',
                1.5:'x',
                2.5:'x'
            }
        },
        {
            'text':'Shut the fuck, the fuck, the fuck, the fuck up.',
            'type':'call',
            'length':8,
            'inputs':{
                0:{"button":"a","sound":"stfu_shut"},
                1:{"button":"b","sound":"stfu_the"},
                1.5:{"button":"x","sound":"stfu_fuck"},
                2.5:{"button":"b","sound":"stfu_the"},
                3.0:{"button":"x","sound":"stfu_fuck"},
                4.0:{"button":"b","sound":"stfu_the"},
                4.5:{"button":"x","sound":"stfu_fuck"},
                5.5:{"button":"b","sound":"stfu_the"},
                6.0:{"button":"x","sound":"stfu_fuck"},
                7.0:{"button":"x","sound":"stfu_up"}
            }
        },
        {
            'text':'Shut the fuck, the fuck, the fuck, the fuck up!',
            'type':'response',
            'length':8,
            'sfx':{
                'a':['pl_stfu_shut'],
                'b':['pl_stfu_the'],
                'x':['pl_stfu_fuck','pl_stfu_up']
            },
            'inputs':{
                0:'a',
                1:'b',
                1.5:'x',
                2.5:'b',
                3.0:'x',
                4.0:'b',
                4.5:'x',
                5.5:'b',
                6.0:'x',
                7.0:'x'
            }
        }
    ]
}

def get_pos_on_tl(surface, length, beat, player):
    # used to find the graphical position on the timeline,
    # based on t, length of bar, and size of surface
    if length <= 4:
        x = (surface.get_width()/17) * (beat*4%16 + 1)
        y = surface.get_height()/4
    else:
        x = (surface.get_width()/17) * (beat*4%16 + 1)
        y = surface.get_height()/6 * (int(beat*4/16)+1)
    y += surface.get_height() / 2 * player
    return [int(x), int(y)]

def draw_dots(surface, length):
    # used for the timeline at the top
    length = int(length * 4)
    for i in range(length):
        radius = 4
        if i % 4 == 0:
            radius = 7
        pygame.draw.circle(surface, [255,255,255], get_pos_on_tl(surface,length/4,i/4,0),radius)
        pygame.draw.circle(surface, [255,255,255], get_pos_on_tl(surface,length/4,i/4,1),radius)
    
class HUDBeat:
    def __init__(self, image, start_time, pos):
        self.image = image
        self.start_time = start_time
        self.pos = pos
        self.surface = pygame.Surface([50,50])
        self.surface.set_colorkey([255,0,255])
        self.surface.fill([255,0,255])

    def update(self, surface, pos):
        t = pos - self.start_time
        extra = 0
        if t < 0.25:
            extra = int(40 * (0.25 - t))
        if t*9 <= math.pi*2:
            temp = pygame.transform.scale(self.image,
                                          [int(math.fabs(math.cos(t*9)*self.surface.get_width()/2))+extra,
                                           int(self.surface.get_height()/2)+extra])
            self.surface.fill([255,0,255])
            self.surface.blit(temp, [self.surface.get_width()/2 - temp.get_width()/2,
                                     self.surface.get_height()/2 - temp.get_height()/2])
        surface.blit(self.surface, [self.pos[0] - self.surface.get_width()/2,
                                    self.pos[1] - self.surface.get_height()/2])
        
        

buttons = {pygame.K_z:'a',pygame.K_x:'b',pygame.K_c:'x',pygame.K_v:'y'}

font_caption = pygame.font.Font("ode_to_idle_gaming.otf", 15)

bump = pygame.mixer.Sound('blip.ogg')
sfx_oops = pygame.mixer.Sound('sfx/oops.wav')
sfx_good = pygame.mixer.Sound('sfx/good.ogg')
glyphs = {
    'a':pygame.image.load('img/button/z.png'),
    'b':pygame.image.load('img/button/x.png'),
    'x':pygame.image.load('img/button/c.png'),
    'y':pygame.image.load('img/button/v.png')
    }
bar_surf = pygame.Surface([500,150])
bar_surf.set_colorkey([255,0,255])
bar_surf.fill([255,0,255])
beats_surf = pygame.Surface([bar_surf.get_width(),bar_surf.get_height()])
beats_surf.set_colorkey([255,0,255])
beats_surf.fill([255,0,255])
clock = pygame.time.Clock()
    
print('Loading song...')
for i in song['sounds']:
    print("SFX:", i, song['sounds'][i])
    temp = pygame.mixer.Sound(song['sounds'][i])
    song['sounds'][i] = temp
captions = []
for i in song['bars']:
    print("Rendering caption:", i['text'])
    captions.append(font_caption.render(i['text'],0,(255,255,255)))


interval = 60 / song['bpm']

pygame.mixer.music.load(song['song'])
pygame.mixer.music.play()

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
    beats_surf.fill([255,0,255])
    
    if bar['type'] == 'call':

        screen.blit(bar_surf,[screen.get_width()/2-bar_surf.get_width()/2,25])
        screen.blit(captions[bar_no],[int(screen.get_width()/2 - captions[bar_no].get_width()/2),int(screen.get_height()*.70)])
        pygame.draw.circle(beats_surf, [255,122,122],
                           get_pos_on_tl(beats_surf,bar['length'],bar_beat,0),
                           10)

        if next_input < len(bar['inputs']):
            target = list(bar['inputs'])[next_input]
            if bar_beat >= target:
                song['sounds'][bar['inputs'][target]['sound']].play() # i've got to make this cleaner
                hud_beats.append(HUDBeat(glyphs[bar['inputs'][target]['button']],
                                         pos,
                                         get_pos_on_tl(bar_surf,bar['length'],target,0)
                                         )
                                 )
                next_input += 1

        if bar_beat >= bar['length']-1 and bar_no + 1 < len(song['bars']):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in buttons:
                        if buttons[event.key] in song['bars'][bar_no+1]['sfx']:
                            if no_presses[0] == buttons[event.key]:      # WHY DID I PASTE THIS A SECOND DAMN TIME THERE HAS GOT TO BE A BETTER WAY TO DO THIS
                                if no_presses[1] < len(song['bars'][bar_no+1]['sfx'][buttons[event.key]])-1:
                                    no_presses[1] += 1
                                else:
                                    no_presses[1] = 0
                            else:
                                no_presses = [buttons[event.key], 0]
                            song['sounds'][song['bars'][bar_no+1]['sfx'][buttons[event.key]][no_presses[1]]].play()
                        else:
                            sfx_oops.play()
                        hud_beats.append(HUDBeat(glyphs[buttons[event.key]],
                                             pos,
                                             get_pos_on_tl(bar_surf,bar['length'],bar_beat,1)
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
                if event.key in buttons:
                    if buttons[event.key] in bar['sfx']:
                        if no_presses[0] == buttons[event.key]:      # THIS IS AWFUL OH MY GOD
                            if no_presses[1] < len(bar['sfx'][buttons[event.key]])-1:
                                no_presses[1] += 1
                            else:
                                no_presses[1] = 0
                        else:
                            no_presses = [buttons[event.key], 0]
                        song['sounds'][bar['sfx'][buttons[event.key]][no_presses[1]]].play()
                    else:
                        sfx_oops.play()
                    hud_beats.append(HUDBeat(glyphs[buttons[event.key]],
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
        bump.play()
        bar_beat_discrete = int(beat) - beats_so_far
        if bar_beat_discrete+1 > bar['length']: # start a new bar
            if bar['type'] == 'response':
                sfx_good.play()
                hud_beats = []
            bar_no += 1
            beats_so_far += bar['length']
            bar = song['bars'][bar_no]
            bar_timestamp = pos
            next_input = 0
            bar_surf.fill([255,0,255])
            draw_dots(bar_surf, bar['length'])
            
    elif pos % interval > interval - interval / 2 and pos % interval < interval - interval / 4 and pulsed:
        pulsed = 0
