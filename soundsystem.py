import pygame as pg
pg.mixer.set_num_channels(32)
class SoundManager():
    def __init__(self,path_to_sound_folder):
        self.hover_sounds = {}
        self.sounds = {}
        self.path_to_sounds = path_to_sound_folder

    def play(self,sound_name,extension='ogg',loop=False,volume = 1):
        if sound_name not in self.sounds:
            self.sounds[sound_name] = {
                'sound': pg.mixer.Sound(f'{self.path_to_sounds}/{sound_name}.{extension}'),
                'played': False
            }
        channel = pg.mixer.find_channel(force=True)
        if self.sounds[sound_name]['played']:
            return
        #self.sounds[sound_name]['sound'].play()
        #channel.play(self.sounds[sound_name]['sound'])
        if not loop:
            self.sounds[sound_name]['sound'].play()
            self.sounds[sound_name]['played'] = True
        if loop:
           channel.play(self.sounds[sound_name]['sound'],loops=-1)
        self.sounds[sound_name]['sound'].set_volume(volume)
    def hover_play(self,sound_name,extension='ogg',is_hover = True):
        if sound_name not in self.hover_sounds:
            self.hover_sounds[sound_name] = {
                    'sound' : pg.mixer.Sound(f'{self.path_to_sounds}/{sound_name}.{extension}'),
                    'played' : False,
                }

        if is_hover and not self.hover_sounds[sound_name]['played']:
            self.hover_sounds[sound_name]['sound'].play()
            self.hover_sounds[sound_name]['played'] = True
        

    def reset_flag(self,is_loop=False):
        for sound in self.sounds.values():
            if is_loop:
                sound['sound'].stop()
        self.sounds.clear()

    def stop(self,sound_name):
        self.sounds[sound_name]['sound'].stop()
    
    def stop_all(self):
        for sound in self.sounds.values():
            sound['sound'].stop()
        self.sounds.clear()   

    def reset_hover_flag(self):
        self.hover_sounds.clear()