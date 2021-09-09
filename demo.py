#testing webhook

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


def draw_dots(surface, length):
    # used for 
    length = int(length * 4)
    if length <= 16:
        for i in range(length):
            x = (surface.get_width()/17) * (i%16+1)
            radius = 5
            if i % 4 == 0:
                radius = 7
            pygame.draw.circle(surface, [255,255,255], [int(x),int(surface.get_height()/4)], radius)
            pygame.draw.circle(surface, [255,255,255], [int(x),int(surface.get_height()/4*3)], radius)
    else:
        for i in range(length):
            x = (surface.get_width()/17) * (i%16+1)
            y = surface.get_height()/6 * (int(i/16)+1)
            radius = 5
            if i % 4 == 0:
                radius = 7
            pygame.draw.circle(surface, [255,255,255], [int(x),int(y)], radius)
            pygame.draw.circle(surface, [255,255,255], [int(x),int(y+surface.get_height()/2)], radius)
		

buttons = {pygame.K_z:'a',pygame.K_x:'b',pygame.K_c:'x',pygame.K_v:'y'}

font_caption = pygame.font.Font("ode_to_idle_gaming.otf", 15)

bump = pygame.mixer.Sound('blip.ogg')
sfx_oops = pygame.mixer.Sound('sfx/oops.wav')
sfx_good = pygame.mixer.Sound('sfx/good.ogg')
bar_surf = pygame.Surface([500,150])
bar_surf.set_colorkey([255,0,255])
bar_surf.fill([255,0,255])
clock = pygame.time.Clock()
    
print('Loading...')
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

while pygame.mixer.music.get_busy():
    clock.tick()
    events = pygame.event.get()
            
    pos = pygame.mixer.music.get_pos() / 1000 - song['offset']
    beat = pos/interval
    bar_beat = (pos-bar_timestamp)/interval
    #pygame.display.set_caption(str(clock.get_fps()))
    
    screen.fill([100,100,100])
    
    if bar['type'] == 'call':

        screen.blit(bar_surf,[screen.get_width()/2-bar_surf.get_width()/2,25])
        screen.blit(captions[bar_no],[int(screen.get_width()/2 - captions[bar_no].get_width()/2),int(screen.get_height()*.70)])

        if next_input < len(bar['inputs']):
            target = list(bar['inputs'])[next_input]
            if bar_beat >= target:
                song['sounds'][bar['inputs'][target]['sound']].play()
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
            

    elif bar['type'] == 'response':
        
        screen.blit(bar_surf,[screen.get_width()/2-bar_surf.get_width()/2,25])
        screen.blit(captions[bar_no],[int(screen.get_width()/2 - captions[bar_no].get_width()/2),int(screen.get_height()*.70)])
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
                
    pygame.draw.circle(screen,(255,255,255), [
        int(screen.get_width()*.25) + (pos/4%interval) * int(screen.get_width()*.50)/interval,
        int(screen.get_height()*.95) - 50*math.fabs(math.sin(math.pi/interval*pos))
        ], 5)
    
    pygame.display.flip()
    if pos % interval < interval / 4 and not pulsed:
        pulsed = 1
        bump.play()
        bar_beat_discrete += 1
        if bar_beat_discrete > bar['length']: # start a new bar
            if bar['type'] == 'response':
                sfx_good.play()
            bar_no += 1
            bar_beat_discrete = 1
            bar = song['bars'][bar_no]
            bar_timestamp = pos
            next_input = 0
            bar_surf.fill([255,0,255])
            draw_dots(bar_surf, bar['length'])
            
    elif pos % interval > interval - interval / 2 and pos % interval < interval - interval / 4 and pulsed:
        pulsed = 0
