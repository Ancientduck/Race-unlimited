

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
        self.chosen_color = 0
        self.colors = {
            'black':{
                'color': (0,0,0)
            },
            'blue':{
                'color': (0,0,255)
            },
            'red':{
                'color':(255,0,0)
            },
            'green':{
                'color':(0,255,0)
            }
        }
    def control(self,screen_size):
        self.screen_width,self.screen_height = screen_size
        # if not self.set:
        #     self.x,self.y = self.screen_width/2,20
        #     self.set = True
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.y -= 10
        elif keys[pg.K_DOWN]:
            self.y += 10
        elif keys[pg.K_LEFT]:
            self.x -= 10
        elif keys[pg.K_RIGHT]:
            self.x += 10



    def debug_on_screen(self,things=None,color=None):
        if things == None:
            return
        self.chosen_color = color

        if color not in self.colors:
            color = 'black'

        self.somethings.append((things,color))
        


    def show_bug(self,screen,screen_size):
        self.control(screen_size) 
     
        if self.somethings:
            for i,(thing,color_key) in enumerate(self.somethings):
                color = self.colors[color_key]['color']  # Random color
                self.text = self.font.render(f'{thing}',True, color)
                screen.blit(self.text,(self.x,self.y+i*20))
            self.somethings.clear()
                
debug = Debug()