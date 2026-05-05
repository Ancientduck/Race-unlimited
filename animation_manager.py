import pygame as pg
class Make_animation:
    def __init__(self):
        self.i = 0
        self.frame = 0
        self.holding_done = False

    def reset(self):
        self.holding_done = False
        self.i = 0
        self.frame = self.i

    def get_frame(self,images,update_interval = 0.3,holding=False,start_again_at=0,one_loop = False):
        the_images = images
    

        if not holding:
           return self.looping_sys_normal(the_images,update_interval,one_loop)
        if holding:
            return self.looping_sys_holding(start_again_at,the_images,update_interval)
    
    def looping_sys_normal(self,the_images,update_interval,one_loop):
        self.i += update_interval
        self.frame = int(self.i)
        if not one_loop:
            if self.frame >= len(the_images):
                self.i = 0
                self.frame = self.i
        elif one_loop:
            if self.frame >= len(the_images):
                return pg.Surface((10,10), pg.SRCALPHA)
            
        frame_image = the_images[self.frame]            
        return frame_image
    
    def looping_sys_holding(self,start_again_at,the_images,update_interval):

        if not self.holding_done:
            self.i += update_interval
            self.frame = int(self.i)

            if self.frame >= len(the_images):
                self.i = start_again_at
                self.frame = self.i
                self.holding_done = True

            frame_image = the_images[self.frame]            
            return frame_image
        if self.holding_done:
            looping_images = the_images
            self.i += update_interval
            self.frame = int(self.i)
            if self.frame >= len(looping_images):
                self.i = start_again_at
                self.frame = self.i

            frame_image = looping_images[self.frame]

            return frame_image
    def reset(self):
        self.i = 0
        self.frame = 0
make_animation = Make_animation()