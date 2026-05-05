import pygame as pg
from kill_bug import debug
from screen_shaker import screen_shake
from soundsystem import SoundManager
import math
import time
the_font = pg.font.Font('Dragrace.ttf',36)
sndmngr = SoundManager('sounds')



class Timer():
    def __init__(self,time_has=60):
        self.starting_time = 3
        self.time_left = 0
        self.time_has = time_has + self.starting_time
        self.dynatime_orignal = pg.image.load('car_assets/dynatime.png')
        self.dynatime = self.dynatime_orignal
        w,h = 400,150
        self.dynatime = pg.transform.scale(self.dynatime_orignal, (w,h))
        self.the_timer = pg.time.get_ticks()/1000

        self.time_paused = False
        self.prev_time = 0

        time_gone = pg.time.get_ticks()/1000 - self.the_timer
        self.time_left = 0
    def pause_time(self):
        self.time_paused = True

    def unpause_time(self):
        self.time_paused = False

    def show_time(self,screen,pos):
        if not self.start_race_time(screen):
            return
        time_gone = pg.time.get_ticks()/1000 - self.the_timer
        #self.the_timer = pg.time.get_ticks()/1000
        if not self.time_paused:
            self.time_left = int(self.time_has-time_gone)
        time_text = the_font.render(f'{self.time_left}',True,(255,0,0))
        if self.time_left < 0:
            time_text = the_font.render(f'DIE',True,(255,0,0))

        dyna_pos = self.dynatime.get_rect(topright=screen.get_rect().topright)
        dyna_rect =  self.dynatime.get_rect(topright=screen.get_rect().topright)

        time_rect_pos_fix_y = 3
        text_rect = time_text.get_rect(midbottom=(dyna_rect.centerx,dyna_rect.centery- time_rect_pos_fix_y))

        if self.time_left < 10:
            screen_shake.object_shake(1,1)

        offsets = screen_shake.object_make()
        screen.blit(self.dynatime,(offsets[0]+dyna_pos[0],(offsets[1]+dyna_pos[1])))
        screen.blit(time_text,(text_rect.x+offsets[0],text_rect.y+offsets[1]))

    
    def add_time(self,amount):
        self.time_has += amount
    
    def pulse(self):
        t = pg.time.get_ticks()/1000
        amount = math.sin(2*math.pi*t)*10
        debug.debug_on_screen(amount)
        return amount
    
    def reset(self, time_has):
        self.time_has = time_has
        self.the_timer = pg.time.get_ticks()/1000
        self.time_left = time_has
    def start_race_time(self,screen):

        the_font = pg.font.Font('Dragrace.ttf',100)
        time_gone = pg.time.get_ticks()/1000 - self.the_timer

        time_left = self.starting_time-int(time_gone)
            
        if time_left < 0:
            return True


        if time_left != self.prev_time:

            sndmngr.play('time_tick','mp3')
            sndmngr.reset_flag()
            
        self.prev_time = time_left

        
        text = the_font.render(f'{time_left}',True,(255,0,0))
        text_rect = text.get_rect(center = screen.get_rect().center)
        if      time_left == 0:
                sndmngr.play('air_horn','mp3')
                new_txt = the_font.render(f'GO',True,(255,0,0))
                text = new_txt
        

        screen.blit(text,text_rect)
