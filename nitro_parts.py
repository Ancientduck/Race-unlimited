import pygame as pg
import math
from animation_manager import make_animation
from kill_bug import debug




def alot_of_images(file_name,file_path,files_num,extension = 'png'):
    images = []
    for i in range(files_num):
        the_file = f'{file_path}/{file_name}_{i}.{extension}'
        image = pg.image.load(the_file)
        images.append(image)
    return images

the_images = alot_of_images('nitro','car_assets/nitro',19)
class Nitro:
    def __init__(self):
        self.images = the_images
        self.base_nitro_filler_size = (70,130)
        self.nitro_tank_Size = (100,200)
        self.nitro_filler_size = self.base_nitro_filler_size

        self.nitro_image = pg.image.load('car_assets/nitro_tank.png')
        self.nitro_image = pg.transform.smoothscale(self.nitro_image,self.nitro_tank_Size )


        self.nitro_filler = pg.Surface(self.base_nitro_filler_size,pg.SRCALPHA)

        self.i = 0
        self.is_active = False
        self.nitro_cheat_on = False
    def give_nitro(self):
        self.current_image = make_animation.get_frame(self.images,0.7,True,10)
        return self.current_image
    def nitro_bar(self,screen,nitro_on:False):
        full_h = self.base_nitro_filler_size[1]
        nitro_filler_w,nitro_filler_h = self.nitro_filler_size
        pos = (screen.get_width()-self.nitro_image.get_width()-10,screen.get_height()-self.nitro_image.get_height()-10)
        filler_pos = (pos[0],pos[1])
        rect = self.nitro_image.get_rect(topleft=pos)

        
        rate_of_change = 0.5
        if nitro_on and nitro_filler_h >= 0:
            nitro_filler_h -= rate_of_change
        elif not nitro_on and nitro_filler_h < self.base_nitro_filler_size[1]:
            nitro_filler_h += rate_of_change 

        if nitro_filler_h <= 0:
            nitro_on = False
            self.is_active = False
            
        else:
            self.is_active = True

        new_nitro_filler_size = (nitro_filler_w,nitro_filler_h)
        self.nitro_filler_size = new_nitro_filler_size

        
        now_nitro_filler = pg.Surface(new_nitro_filler_size,pg.SRCALPHA)
        filler_rect = now_nitro_filler.get_rect(midbottom=(rect.midbottom[0],rect.midbottom[1]-10))
          # Start drawing from here
        
        for i in range(int(nitro_filler_h)):
            color_value = int((i / full_h) * 255)
            color = (color_value, 0, 0)
            pg.draw.line(now_nitro_filler, color, (0,i), (nitro_filler_w, i))
                

        pulse = int(50 * math.sin(pg.time.get_ticks() * 0.01))
        nitro_on_highlight = pg.Surface(self.nitro_filler_size, pg.SRCALPHA)
        nitro_on_highlight.fill((255, 0, 0, 200 + pulse))

        
        if nitro_on:
            screen.blit(now_nitro_filler, filler_rect)
        else:
            screen.blit(now_nitro_filler,filler_rect)

        screen.blit(self.nitro_image,rect)
    
    def reset(self):
        make_animation.reset()
nitro = Nitro()

