import pygame as pg
import random
from kill_bug import debug


#Initialize Pygame

pg.init()
screen = pg.display.set_mode((800, 600))
clock = pg.time.Clock()

class Trail():
    def __init__(self,color):
        self.width,self.height = screen.get_size()

        
        self.x = 0
        self.y = 0

        edge = random.choice([0, 1, 2, 3])
    
        if edge == 0:  # Left edge
            self.x = 0
            self.y = random.randint(0, self.height)
        elif edge == 1:  # Right edge
            self.x = self.width
            self.y = random.randint(0, self.height)
        elif edge == 2:  # Top edge
            self.x = random.randint(0, self.width)
            self.y = 0
        else:  # Bottom edge
            self.x = random.randint(0, self.width)
            self.y = self.height

        self.directions = [(1,0), (-1,0), (0,1), (0,-1)]
        self.chosen_direction = random.choice(self.directions)
        self.new_x,self.new_y = 0,0
        self.color = color

        self.frame_counter = 0

    def get_directions(self):
        if random.randint(1,100) == 2:
            self.chosen_direction = random.choice(self.directions)
        return self.chosen_direction
    def get_line_data(self):

        speed = 1


        dx,dy = self.get_directions()
        self.x += dx*speed
        self.y += dy*speed

        

        if self.x <= 0:  
            self.x = self.width
        if self.y <= 0: 
            self.y = self.height
        if self.x > self.width:
            self.x = 0
        if self.y > self.height:
            self.y = 0

    

        return self.x,self.y,dx,dy

red,green,blue = (255,0,0),(0,255,0),(0,0,255)
class MakeTrail:
    def __init__(self,how_many_lines = 50 ,screen_size=(1920,1080)):
        self.screen = screen
        self.lines_data = [Trail(red,) for i in range(how_many_lines)]
        self.trail_surface = pg.Surface(screen_size, pg.SRCALPHA)
        self.fade_surface = pg.Surface(screen_size, pg.SRCALPHA)
        self.frame_counter = 0  
        self.color = red
    def draw_lines(self):

        #glow = pg.draw.circle(glow_surface,(*self.color,60),end_pos,5,5)

        self.frame_counter  += 1
        if self.frame_counter >= 2:

                self.fade_surface.fill((0, 0, 0, 1))  
                self.trail_surface.blit(self.fade_surface,(0,0), special_flags=pg.BLEND_RGBA_SUB)
                self.frame_counter = 0
        for trail in self.lines_data:
            self.color = red

            


            x,y,dx,dy = trail.get_line_data()
            end_pos = (x,y)



            circle_width = 3
            head_pos = 4+circle_width

            #head_circle = pg.draw.circle(screen,(self.color),(end_pos[0]+dx*head_pos,end_pos[1]+dy*head_pos),7,circle_width)

        # glow = pg.draw.circle(glow_surface,(*self.color,60),end_pos,5,5)

            pg.draw.circle(self.trail_surface,(*self.color,255),end_pos,2,2)

            
            circle_width = 3
            head_pos = 4+circle_width

            head_circle = pg.draw.circle(screen,(self.color),(end_pos[0]+dx*head_pos,end_pos[1]+dy*head_pos),7,circle_width)

        screen.blit(self.trail_surface,(0,0))


drawline = MakeTrail(screen_size=(800,600))
num = 100
trail_list = [Trail(red) for i in range(num)]


running = True

#frame_counter = 0
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    screen.fill((0, 0, 0))
    

    drawline.draw_lines()
    
    
    
    # Randomly change direction sometimes
    fps = clock.get_fps()
    debug.debug_on_screen(fps,'blue')
    
    debug.show_bug(screen,screen.get_size())
    pg.display.flip()
    clock.tick(100)

pg.quit()
#? make it a module