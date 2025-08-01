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

selected_map = 'river'
#test
#loop
#river
#city #not good
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
        self.friction = 500
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


        #drift
        self.velocity = pg.Vector2(0,0)
        self.brake_drift = False
        self.drift_factor = 0.8 # more is more drift 
        self.new_drift = self.drift_factor
       #  self.facing_angle = 0


        self.friction_off_road = 0.05
    def rotate_car(self,rotation_speed):
        self.keys = pg.key.get_pressed()
        speed_loss_amount = self.acceleration*dt
        speed_loss = 0
        speed_loss_start_speed = self.now_max_speed/2
        self.speed = self.velocity.length()
        if self.keys[pg.K_a]:
            self.angle += rotation_speed
            if self.speed > speed_loss_start_speed:  
                speed_loss += speed_loss_amount
                self.speed -= (self.acceleration+speed_loss) *dt

        if self.keys[pg.K_d]:
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
        
        return self.pixel_color == 1

        
    def drift(self, vector, velocity, drifting):
        forward = vector * velocity.dot(vector)
        lateral = velocity - forward
        
        # Grip should be inverse of drift
        grip = 1.0 - drifting
        
        # Keep all forward velocity, reduce lateral based on grip
        v = forward + lateral * grip

        return v
        

    def movement(self):
        
        rotation_speed = self.rotation_speed
        #new_speed = self.max_speed
        self.keys = pg.key.get_pressed()

        #self.new_drift = 0

        rad = math.radians(self.angle)
    
        dx = math.cos(rad)
        dy = -math.sin(rad)

        forward = pg.Vector2(dx,dy)
        
            
        
        if self.keys[pg.K_SPACE]:
            if self.velocity.length() > 0:
                friction_force = self.velocity.normalize() * -dt * self.acceleration*1.6
                self.velocity += friction_force
                #debug.debug_on_screen(f' speed stopping power: {friction_force} ' )
                # Stop if speed gets too low
                if self.velocity.length() < 15:
                    self.velocity = pg.Vector2(0, 0)
            
            max_drift = 0.3
            if self.new_drift > max_drift:
                self.new_drift -= 0.05  # LOW = more sli   p

            rotation_speed *= 1.6
            if self.speed > 0:
                self.rotate_car(rotation_speed)
        else:
            if self.new_drift < self.drift_factor:
                self.new_drift += 0.02
                  # recover grip gradually
                
           # self.new_drift = self.drift_factor  # default value
       # debug.debug_on_screen(self.new_drift,'blue')
        

        if self.keys[pg.K_w]:
            self.velocity += self.acceleration * dt*forward
            if self.speed < 0:
                self.speed += (5*self.acceleration) *dt
            self.rotate_car(rotation_speed)

        elif self.keys[pg.K_s]:
            way = self.velocity.dot(forward)
           # debug.debug_on_screen(way,'red')
            if way > -500:
                self.velocity -= self.brake*forward
            if self.speed > self.max_speed/2:
                self.rotate_car(rotation_speed * 1.4)
            self.rotate_car(rotation_speed)
        else:
            #friction
            self.speed = self.velocity.length()

            if self.speed > 0:
                friction_force = self.velocity.normalize() * -self.friction
                self.velocity += friction_force*dt
                if self.speed <15:
                    self.velocity = pg.Vector2(0,0)        
            
            if self.speed > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)
            
            if self.speed > 0:
                self.rotate_car(rotation_speed * 1.3)
            if self.speed < 0:
                self.speed += self.friction
                self.rotate_car(rotation_speed)

        # thing1 = f'the vector velocity: {self.velocity}'
        # thing2 = f'SPEED: {self.speed}'
        
        # debug.debug_on_screen(thing1,'blue')
        # debug.debug_on_screen(thing2,'black')
        
         # ===== drifting part ====

        self.velocity = self.drift(forward,self.velocity,(self.drift_factor*self.new_drift))
        
         

                                            ### MAKING DRIFT LOGIC
        self.x += self.velocity.x *dt ## MOVES THE CAR
        self.y += self.velocity.y *dt

        self.rotated_image = pg.transform.rotate(self.image,(self.angle))
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    
        self.rect.center = (self.x, self.y)
        self.rect.clamp_ip(self.map.get_rect())
        self.x, self.y = self.rect.center

        if not self.on_road():
            #debug.debug_on_screen(self.pixel_color,'black')
            #debug.debug_on_screen(f'no on road','red')
            self.speed = self.velocity.length()
            if self.speed > self.max_speed/3:
                off_road_fiction = self.velocity.normalize()*-self.friction*20
                self.velocity += off_road_fiction *dt


        self.speed = self.velocity.length()

        #thing = f"current_speed :{int(self.speed)} ,  current_angle:{int(self.angle)}"
       # debug.debug_on_screen(thing)

       
    
        
    def draw_map(self,camera_x,camera_y):
        screen.blit(self.map, (-camera_x,-camera_y))


    def draw(self):

        
        self.movement()

        camera_x,camera_y =camera(self.x,self.y,screen_size,self.map_size) #sets the camera

        self.draw_map(camera_x,camera_y)

        
        
        car_screen_x = self.x - camera_x
        car_screen_y = self.y - camera_y
        self.car_pos = self.rotated_image.get_rect(center=(car_screen_x,car_screen_y))

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