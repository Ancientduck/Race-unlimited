

import pygame as pg
import random
pg.init()

class Debug():
    def __init__(self,):
        self.x,self.y = 0,0
        self.set = False
        self.color_set = False
        self.text = None
        self.color = (0)
        self.font = pg.font.SysFont('consolas  ',24,bold=True) 
        self.somethings = [] 
        self.colors = {}
    def control(self,screen_size):
        self.screen_width,self.screen_height = screen_size
        # if not self.set:
        #     self.x,self.y = self.screen_width/2,20
        #     self.set = True
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.y -= 1
        elif keys[pg.K_DOWN]:
            self.y += 1
        elif keys[pg.K_LEFT]:
            self.x -= 1
        elif keys[pg.K_RIGHT]:
            self.x += 1



    def debug_on_screen(self,things=None):
        if things == None:
            return
        
       # if text == None:
       #     text = " "

        self.somethings.append((things))
        


    def show_bug(self,screen,screen_size):
        self.control(screen_size) 
     
        if self.somethings:
            for i,(thing) in enumerate(self.somethings):
                if i not in self.colors:
                    self.colors[i] = (random.randint(155, 255), random.randint(0, 255), random.randint(0, 255))  # Random color
                
                self.text = self.font.render(f'{thing}',True, self.colors[i])
                screen.blit(self.text,(self.x,self.y+i*20))
            self.somethings.clear()
                
debug = Debug()