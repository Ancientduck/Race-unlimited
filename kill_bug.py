

import pygame as pg

class Debug():
    def __init__(self,):
        self.x,self.y = 0,0
        self.set = False
        self.text = None
    def control(self,screen_size):
        self.screen_width,self.screen_height = screen_size
        if not self.set:
            self.x,self.y = self.screen_width/2,20
            self.set = True
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.y -= 1
        elif keys[pg.K_DOWN]:
            self.y += 1
        elif keys[pg.K_LEFT]:
            self.x -= 1
        elif keys[pg.K_RIGHT]:
            self.x += 1



    def debug_on_screen(self,thing=None,screen_size=None,text=None):
        if thing == None:
            return
        if text == None:
            text = " "
        self.control(screen_size)
        self.screen_width,self.screen_height = screen_size
        font = pg.font.SysFont(None,24)
        self.text = font.render(f'{text} {thing}',True, (255,0,0))


    def show_bug(self,screen):
        if self.text:
            screen.blit(self.text,(self.x,self.y))

debug = Debug()