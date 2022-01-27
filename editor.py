from glob import glob
from os.path import basename, splitext
import json, time
import pygame
import misc, ui
from constants import *

class EditorManager:
    def __init__(self, chart = None):
        self.path = ""
        self.song = {"bars":[]}
        self.sounds = {}
        self.bar_no = 0
        self.cursor = 0
        self.sfxMenuPos = 0
        self.sfxMenuPosLast = 0
        self.t = time.time()*2
        self.beats = []
        self.increment = 0.25
        self.bar = None

        self.glyphs = [i for i in ui.glyphs]
        self.selectedGlyph = 0
        self.selectedSound = "None"

        self.tl_dots_surf = pygame.Surface([2*ui.screensize[0]/3 - 20, ui.tl_size[1]]).convert_alpha(ui.screen_surface)
        self.tl_dots_surf.fill(ui.alpha)
        self.sfxListSurface = pygame.Surface([ui.screensize[0]/3, ui.screensize[1]]).convert_alpha(ui.screen_surface)
        self.sfxListSurface.fill(ui.alpha)
        self.bar_header = pygame.Surface([0,0])
        self.sound_header = ui.font_caption.render(self.selectedSound, 0, [255, 255, 255])
        
        self.menu = ui.ButtonMenu()
        self.menu.addButton('bar_prev', '<', [self.sfxListSurface.get_width() + 20, 20], [30,30], self.navigateBars, [-1])
        self.menu.addButton('bar_next', '>', [ui.screensize[0] - 20, 20], [30,30], self.navigateBars, [1])
        self.glyphUIPos = [self.sfxListSurface.get_width() + 20, ui.screensize[1]/4 + ui.tl_size[1]/2 + 20]
        self.menu.addButton('glyph_prev', '<', self.glyphUIPos, [30,30], self.navigateGlyphs, [-1])
        self.menu.addButton('glyph_next', '>', [self.glyphUIPos[0]+60, self.glyphUIPos[1]], [30,30], self.navigateGlyphs, [1])
        self.menu.addButton('add_beat', '+', [self.glyphUIPos[0]+90, self.glyphUIPos[1]], [30,30], self.addBeatAtCursor)
        self.menu.addButton('remove_beat', '-', [self.glyphUIPos[0]+120, self.glyphUIPos[1]], [30,30], self.deleteBeatAtCursor)
        self.glyphBeat = ui.HUDBeat(self.glyphs[self.selectedGlyph], self.t, [self.glyphUIPos[0]+30, self.glyphUIPos[1]])

        self.menu.addButton('save_chart', 'Save', [ui.screensize[0] - 45, ui.screensize[1] - 20], [70,30], self.saveChart)
        self.menu.addButton('return_to_menu', 'Exit', [ui.screensize[0] - 125, ui.screensize[1] - 20], [70,30])
        
        self.sfxList = ui.ButtonMenu()

        if chart:
            self.loadChart(chart)

    def update(self, events):
        
        self.t = time.time()*2
        [beat.update(self.t) for beat in self.beats]
        self.glyphBeat.update(self.t)
        for event in events:
            self.sfxList.handleEvent(event)
            self.menu.handleEvent(event)
            if event.type == pygame.KEYDOWN:
                target = self.cursor
                bar_length = self.bar['length']
                if misc.binds.get(event.key, None) == 'left':
                    target -= self.increment
                if misc.binds.get(event.key, None) == 'right':
                    target += self.increment
                if target >= 0 and target < bar_length:
                    self.cursor = target 

    def draw(self, screen):
        screen.fill([122,122,122])
        
        self.sfxListSurface.fill([100,100,100])
        self.sfxList.draw(self.sfxListSurface)
        screen.blit(self.sfxListSurface, [0, 0-self.sfxMenuPos])

        try:
            bar_length = self.bar['length']
        except:
            bar_length = 0
        ui.draw_dots(self.tl_dots_surf, bar_length, 0)
        ui.draw_dots(self.tl_dots_surf, bar_length, 1)
        cursor_pos = ui.get_pos_on_tl(self.tl_dots_surf, bar_length, self.cursor, 1 if self.bar['type'] == 'response' else 0)
        if not self.bar['type'] == 'break':
            pygame.draw.line(self.tl_dots_surf, [255,255,0], [cursor_pos[0], cursor_pos[1]+15], [cursor_pos[0], cursor_pos[1]-15], 3)
        [beat.draw(self.tl_dots_surf) for beat in self.beats]
        self.glyphBeat.draw(screen)
        screen.blit(self.tl_dots_surf, [2*ui.screensize[0]/3 - self.tl_dots_surf.get_width()/2, ui.screensize[1]/4 - ui.tl_size[1]/2])
        
        screen.blit(self.bar_header, [2*ui.screensize[0]/3 - self.bar_header.get_width()/2, 20 - self.bar_header.get_height()/2])
        screen.blit(self.sound_header, [self.glyphUIPos[0]+140, self.glyphUIPos[1]-self.sound_header.get_height()/2])
        self.menu.draw(screen)

    def drawGL(self):
        pass

    def drawOverGL(self):
        pass

    def loadChart(self, path):
        path = path.strip("/")
        self.path = path
        print("loading", path)
        self.sfxList.removeAllButtons()
        self.sfxMenuPos = 0
        pygame.mixer.music.load(path + "/music.mp3")
        with open(path + "/chart.json") as f:
            self.song = json.loads(f.read())
            f.close()
        self.sounds = {splitext(basename(i))[0]: pygame.mixer.Sound(i) for i in glob(path + "/sfx/*")}

        self.sfxListSurface = pygame.Surface([ui.screensize[0]/3, max(32*len(self.sounds), ui.screensize[1])]).convert_alpha(ui.screen_surface)
        self.sfxListSurface.fill(ui.alpha)
        index = 0
        for sound in self.sounds:
            self.sfxList.addButton("sfx_"+sound, sound, [int(self.sfxListSurface.get_width()/2), int(32*index + 18)], [self.sfxListSurface.get_width(), 30])
            self.sfxList.setButtonFunc("sfx_"+sound, func=self.selectSound, args=[sound])
            index += 1
        self.loadBar(0)

    def loadBar(self, index):
        self.bar_no = index
        self.beats = []
        self.cursor = 0
        self.bar = self.song['bars'][index] if index in range(len(self.song['bars'])) \
                   else {'text':'','type':'break','length':1}
                   
        if self.bar['type'] != 'break':
            player = 0 if self.bar['type'] == 'call' else 1
            ui.draw_dots(self.tl_dots_surf, self.bar['length'], player)
            for beat in self.bar['inputs']:
                pos = ui.get_pos_on_tl(self.tl_dots_surf, self.bar['length'], beat['beat'], player)
                self.beats.append(ui.HUDBeat(beat['button'], self.t, pos))

        self.bar_header = ui.font_caption.render('Bar ' + str(index) + ': ' + self.bar['type'], 0, [255, 255, 255])
    def navigateBars(self, delta):
        if self.bar_no + delta in range(len(self.song['bars'])):
            self.loadBar(self.bar_no + delta)

    def navigateGlyphs(self, delta):
        target = self.selectedGlyph + delta
        g_no = len(self.glyphs)
        if target >= g_no:
            target -= g_no
        elif target < 0:
            target += g_no
        self.selectedGlyph = target
        self.glyphBeat = ui.HUDBeat(self.glyphs[self.selectedGlyph], self.t, [self.glyphUIPos[0]+30, self.glyphUIPos[1]])

    def selectSound(self, sound):
        self.sounds[sound].play()
        self.selectedSound = sound
        self.sound_header = ui.font_caption.render(sound, 0, [255, 255, 255])

    def deleteBeatAtCursor(self):
        if self.bar['type'] != 'break':
            cursor_pos = ui.get_pos_on_tl(self.tl_dots_surf, self.bar['length'], self.cursor, 1 if self.bar['type'] == 'response' else 0)
            [self.beats.remove(i) for i in self.beats if i.pos == cursor_pos]
            [self.song['bars'][self.bar_no]['inputs'].remove(i) for i in self.song['bars'][self.bar_no]['inputs'] if i['beat'] == self.cursor]
        self.bar = self.song['bars'][self.bar_no]

    def addBeatAtCursor(self):
        if self.bar['type'] != 'break':
            if self.selectedSound == 'None' or self.cursor in [i['beat'] for i in self.bar['inputs']]:
                return
            cursor_pos = ui.get_pos_on_tl(self.tl_dots_surf, self.bar['length'], self.cursor, 1 if self.bar['type'] == 'response' else 0)
            index = 0
            new_input = {"beat": self.cursor, "button": self.glyphs[self.selectedGlyph]}
            if self.bar['type'] == 'call':
                new_input['sound'] = self.selectedSound
            self.bar['inputs'].append(new_input)
            self.song['bars'][self.bar_no]['inputs'] = sorted(self.bar['inputs'], key=lambda d: d['beat'])
            self.bar = self.song['bars'][self.bar_no]
            self.beats.append(ui.HUDBeat(new_input['button'], self.t, cursor_pos))

    def increaseBarLength(self):
        self.song['bars'][self.bar_no]['length'] += self.increment
        self.loadBar(self.bar_no)
        
    def decreaseBarLength(self):
        self.song['bars'][self.bar_no]['length'] -= self.increment
        self.loadBar(self.bar_no)

    def saveChart(self):
        with open(self.path + '/chart.json', 'w') as f:
            json.dump(self.song, f)
        print("Chart saved")
