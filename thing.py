import pygame as pg
import time 
import sys
import math
import cv2
import numpy as np

from factory import garage,maps
from kill_bug import debug
from camera import camera
pg.init()

#debug

#the screen things
clock = pg.time.Clock()
screen_width,screen_height = 1920,1000
screen_size = screen_width,screen_height
screen = pg.display.set_mode((screen_width,screen_height))
pg.display.set_caption('racing')


selected_car = 'BMW' 
#glinton
#lamborghini
#esquire
#aston_martin
#pony
#BMW
selected_map = 'loop'

bg_image = pg.image.load(maps[selected_map]['map']).convert()
bg_image = pg.transform.scale(bg_image, (screen_width,screen_height))






class Car():
    def __init__(self,width,height,image,acceleration,max_speed,brake,handling):
        global dt,selected_map
        self.width = width
        self.height = height
        self.image = image
        self.image = pg.image.load(self.image).convert_alpha()
        self.image = pg.transform.scale(self.image, (self.width,self.height))
        self.rect = self.image.get_rect()

       

        zoom = 4
        self.acceleration =  acceleration
        self.friction = 5
        self.speed = 0
        self.direction = 0
        self.max_speed = max_speed
        self.now_max_speed = max_speed
        self.brake = brake
        self.rotation_speed = handling

        self.rotated_image = self.image
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
        self.angle = 0

        self.road_image = pg.image.load(maps[selected_map]['road']).convert()
        self.road_image = pg.transform.scale(self.road_image, (int(self.road_image.get_width()*zoom), int(self.road_image.get_height()*zoom)))
        self.road = pg.mask.from_threshold(self.road_image,(255,255,255),(1,1,1))
        
        self.map = pg.image.load(maps[selected_map]['map']).convert()
        self.map = pg.transform.scale(self.map, (int(self.map.get_width()*zoom), int(self.map.get_height()*zoom)))
        
        self.map_size = self.map.get_width(),self.map.get_height()

        self.x,self.y = self.find_Spawn()
        self.x *= zoom
        self.y *= zoom
       # self.x,self.y = 0,0
        self.camera_x = self.x - screen_width//2
        self.camera_y = self.y - screen_height//2

    def rotate_car(self,rotation_speed):
        keys = pg.key.get_pressed()
        speed_loss_amount = self.acceleration*0.1
        speed_loss = 0
        speed_loss_start_speed = self.now_max_speed/2
        if keys[pg.K_a]:
            self.angle += rotation_speed
            if self.speed > speed_loss_start_speed:  
                speed_loss += speed_loss_amount
                self.speed -= (self.acceleration+speed_loss) *dt

        if keys[pg.K_d]:
            self.angle -= rotation_speed
            if self.speed > speed_loss_start_speed:
                speed_loss += speed_loss_amount
                self.speed -= (self.acceleration+speed_loss) *dt


    def find_Spawn(self): #trying the new thing. getting numpy error axis aerror 2 is out of bounds
         # Load image
        image = maps[selected_map]['road']
        im = cv2.imread(image)

        # Define the blue colour we want to find - remember OpenCV uses BGR ordering
        red = [0,0,255]


        # Get X and Y coordinates of all red pixels
        Y,X = np.where(np.all(im==red,axis=2))
        
        return X[0],Y[0]

    def on_road(self):
        road_color = (195, 195, 195)
        white = (255,255,255)
        black = (0,0,0)
        red = (255,0,0)
        self.pixel_color = self.road.get_at((int(self.x),int(self.y)))
        self.spawn_color_check = self.road_image.get_at((int(self.x),int(self.y)))
        debug.debug_on_screen(self.spawn_color_check)
        return self.pixel_color == 1

    

    

    def movement(self):
        
        rotation_speed = self.rotation_speed
        #new_speed = self.max_speed
        keys = pg.key.get_pressed()

        

        rad = math.radians(self.angle)
    
        dx = math.cos(rad)
        dy = -math.sin(rad)

        if keys[pg.K_SPACE]:  # Handbrake
            self.speed *= 0.95  # simulate drift/slip
           
            rotation_speed *= 4  # much tighter turns
            if self.speed > 0:
                self.rotate_car(rotation_speed)
                self.speed -= self.friction
    
        elif keys[pg.K_w]:
            self.speed += self.acceleration * dt
            if self.speed < 0:
                self.speed += (5*self.acceleration) *dt
            self.rotate_car(rotation_speed)

        elif keys[pg.K_s]:
            self.speed -= self.brake
            if self.speed > 0:
                self.rotate_car(rotation_speed * 3)
            self.rotate_car(rotation_speed)

        else:
            if self.speed > 0:
                self.speed -= self.friction
                if self.speed < 0:
                    self.speed = 0
            if self.speed > 0:
                self.rotate_car(rotation_speed * 2)
            if self.speed < 0:
                self.speed += self.friction
                self.rotate_car(rotation_speed)
                
            # === Clamp Speed ===
        #self.speed = max(0, min(self.speed, self.max_speed))

        if self.speed > self.max_speed:
            self.speed = self.max_speed
        elif self.speed < -self.max_speed:
            self.speed = -self.max_speed

        self.x += self.speed*dt*dx
        self.y += self.speed*dt*dy

        self.rotated_image = pg.transform.rotate(self.image,(self.angle))
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    
        self.rect.center = (self.x, self.y)
        self.rect.clamp_ip(self.map.get_rect())
        self.x, self.y = self.rect.center

        if not self.on_road():
            if self.speed > 300 and self.speed > 0 :
                self.speed -= self.acceleration*5*dt



        thing = f"current_speed :{int(self.speed)} ,  current_angle:{int(self.angle)}"
        thing3 = 'yo'
        debug.debug_on_screen(thing)
        debug.debug_on_screen(thing3)
       
    
        
    def draw_map(self,camera_x,camera_y):
        screen.blit(self.map, (-camera_x,-camera_y))


    def draw(self):

        
        self.movement()

        camera_x,camera_y =camera(self.x,self.y,screen_size,self.map_size) #sets the camera

        self.draw_map(camera_x,camera_y)

        
        
        car_screen_x = self.x - camera_x
        car_screen_y = self.y - camera_y
        self.car_pos = self.rotated_image.get_rect(center=(car_screen_x,car_screen_y))
        #screen.blit(self.rotated_image,(self.rotated_rect))
        screen.blit(self.rotated_image, (self.car_pos))




player_car = Car(**garage[selected_car])

def draw_all():
   # background()
    player_car.draw()
    

running = True

while running:
   # global dt
    dt = clock.tick(100)/1000

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False



    draw_all()

    debug.show_bug(screen,screen_size)

    pg.display.flip()
    clock.tick(100)


pg.quit()
sys.exit()