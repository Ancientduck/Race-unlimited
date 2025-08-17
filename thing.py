import pygame as pg
import time 
import sys
import math
import cv2
import numpy as np

from pprint import pprint

from factory import garage,maps
from kill_bug import debug
from camera import camera
from get_offset_for_mask import get_offset
from collision_detection import collision_check,get_around_points

pg.init()
pg.mixer.init()
#debug

#the screen things
clock = pg.time.Clock()
screen_width,screen_height = 1920,1000
screen_size = screen_width,screen_height
screen = pg.display.set_mode((screen_width,screen_height))
pg.display.set_caption('racing')


selected_car = 'BMW' 
the_font = 'Dragrace.ttf'
#glinton
#lamborghini
#esquire
#aston_martin
#pony
#BMW

selected_map = 'high_way'
#test
#loop
#river
#city #not good
#village
#high_way 

bg_image = pg.image.load(maps[selected_map]['map']).convert_alpha()
bg_image = pg.transform.scale(bg_image, (screen_width,screen_height))




def check_zoom():
        # Load actual map
    raw_map = pg.image.load(maps[selected_map]['map'])
    map_width = raw_map.get_width()
    map_height = raw_map.get_height()

    # Reference map stats
    ref_width = 1914
    ref_height = 935
    ref_zoom = 12

    # Calculate average sizes
    ref_avg = (ref_width + ref_height) / 2
    map_avg = (map_width + map_height) / 2
    
    
    # Calculate scale ratio
    scale_ratio = ref_avg / map_avg

    # Final zoom
    zoom =  (scale_ratio)*ref_zoom
    return zoom

class Car():
    def __init__(self,width,height,image,acceleration,max_speed,brake,handling):
        global dt,selected_map
        self.width = width
        self.height = height
        self.image = image
        self.image = pg.image.load(self.image).convert_alpha()
        self.image = pg.transform.scale(self.image, (self.width,self.height))
        self.car_mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

       

        self.zoom = check_zoom()
        
        self.original_acceleration = acceleration
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

        self.road_image = pg.image.load(maps[selected_map]['road']).convert_alpha()
        self.road_image = pg.transform.scale(self.road_image, (int(self.road_image.get_width()*self.zoom), int(self.road_image.get_height()*self.zoom)))
        self.road = self.road_image
        
        self.map = pg.image.load(maps[selected_map]['map']).convert_alpha()
        self.map = pg.transform.scale(self.map, (int(self.map.get_width()*self.zoom), int(self.map.get_height()*self.zoom)))
        
        self.map_size = self.map.get_width(),self.map.get_height()


        self.x,self.y = self.find_Spawn()
        self.x *= self.zoom
        self.y *= self.zoom
       # print(self.map_size)
       # self.x,self.y = 0,0
        self.camera_x = self.x - screen_width//2
        self.camera_y = self.y - screen_height//2


        #drift
        self.velocity = pg.Vector2(0,0)
        self.brake_drift = False
        self.drift_factor = 0.3 # more is more grip 
        self.new_drift = self.drift_factor

        speed_meter_Size = 200,200
        self.speed_meter_image = pg.image.load('speed_meter.png')
        self.speed_meter_image = pg.transform.scale(self.speed_meter_image,(speed_meter_Size))             

    def find_Spawn(self): #//trying the new thing. getting numpy error axis aerror 2 is out of bounds
         # Load image
        image = maps[selected_map]['road']
        im = cv2.imread(image)

        # Define the RED colour we want to find - remember OpenCV uses BGR ordering
        red = [0,0,255]


        # Get X and Y coordinates of all red pixels
        Y,X = np.where(np.all(im==red,axis=2))
        
        return X[0],Y[0]

    def is_on(self):
        self.pixel_color = self.road.get_at((int(self.x),int(self.y)))
        return self.pixel_color[:3]

        
    def drift(self, vector, velocity, drifting):
        forward = vector * velocity.dot(vector)
        lateral = velocity - forward
        
        # Grip should be inverse of drift
        grip = 1.0 - drifting
        
        # Keep all forward velocity, reduce lateral based on grip
        v = forward + lateral * grip

        return v
        
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


    def screen_collision_check(self,vector,car_rect):
        screen_rect = screen.get_rect()

        if not screen.get_rect().contains(car_rect):
            # Car is touching or outside the screen edges
            collision_results = collision_check.push(self.x, self.y,self.angle,self.velocity.x, self.velocity.y, vector, dt, 500)
            self.x = collision_results[0]
            self.y = collision_results[1]
            self.velocity.x = collision_results[3]
            self.velocity.y = collision_results[4]

            
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
                friction_force = self.velocity.normalize() * -dt * self.acceleration*1.05
                self.velocity += friction_force
                
                if self.velocity.length() < 15:
                    self.velocity = pg.Vector2(0, 0)
            
            max_drift = 0.1
            if self.new_drift > max_drift:
                self.new_drift -= 0.05  # LOW = more sli   p

            rotation_speed *= 1.5
            if self.speed > 0:
                self.rotate_car(rotation_speed)
        else:
            if self.new_drift < self.drift_factor:
                self.new_drift += 0.02
                  # recover grip gradually
                
           
        
        if self.speed > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        if self.keys[pg.K_w]:
            car_sounds.car_accelerating = True
            self.velocity += self.acceleration * dt*forward
            car_sounds.car_sound_sys()

            if self.speed < 0:
                self.speed += (5*self.acceleration) *dt
            self.rotate_car(rotation_speed)


            

        elif self.keys[pg.K_s]:
            speed_by_direction = self.velocity.dot(forward)
            reverse_speed = -self.max_speed/4
            if speed_by_direction > reverse_speed:
                self.velocity -= self.brake*forward
            if self.speed > self.max_speed/2:
                self.rotate_car(rotation_speed * 1.4)
            self.rotate_car(rotation_speed)
        

        

        else:
            
            self.not_accelerating(rotation_speed)
            
        


        if self.acceleration > 0:
                acceleration_modifer = (self.speed/self.max_speed)*self.original_acceleration

                self.acceleration = self.original_acceleration - acceleration_modifer
      

        self.velocity = (self.drift(forward,self.velocity,(self.drift_factor*self.new_drift)))
        
         
        
        self.x += self.velocity.x *dt ## MOVES THE CAR
        self.y += self.velocity.y *dt

        self.rotated_image = pg.transform.rotate(self.image,(self.angle))
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

        self.car_image = self.rotated_image
        self.car_mask = pg.mask.from_surface(self.car_image)   # the masks
        self.car_rect = self.rect

        self.rect.center = (self.x, self.y)
        self.rect.clamp_ip(self.map.get_rect())
        self.x, self.y = self.rect.center
        
    
        self.logics()
        self.speed = self.velocity.length()
        
        
        
        # thing = f"current_speed :{int(self.speed)} ,  current_angle:{int(self.angle)}"

        # debug.debug_on_screen(thing)


        # debug.debug_on_screen(f'the way: {self.velocity.dot(forward)}','green')
        # debug.debug_on_screen(f'rotation_power:{rotation_speed}','blue')

        # thing1 = f'the vector velocity: {self.velocity}'
        # thing2 = f'SPEED: {self.speed}'
    
        # debug.debug_on_screen(thing1,'blue')
        # debug.debug_on_screen(thing2,'black')

        # self.new_drift = self.drift_factor  # default value
        # debug.debug_on_screen(self.new_drift,'blue')





    def not_accelerating(self,rotation_speed):
        self.speed = self.velocity.length()
        
        #====flags for sounds====#

        car_sounds.sounds['car_moving_loop']['played'] = False


        # for sounds in car_sounds.sounds:
        #    car_sounds.sounds[sounds]['played'] = False


        for sounds in car_sounds.loops:
            car_sounds.loops[sounds]['played'] = False            
        
        for gear in ['gear_1', 'gear_2', 'gear_3', 'gear_4']:
            car_sounds.sounds[gear]['played'] = False
        
        
        for sounds in car_sounds.sounds:
            car_sounds.sounds[sounds]['played'] = False

        car_sounds.channel_accel.stop()
        car_sounds.channel_accel_loop.stop()
        car_sounds.channel_gear.stop()
        car_sounds.channel_loop.stop()

        if self.speed > 0:
            friction_force = self.velocity.normalize() * -self.friction
            self.velocity += friction_force*dt
            minumum_speed_for_friction = 15
            if self.speed < minumum_speed_for_friction:
                self.velocity = pg.Vector2(0,0)      

        #if W is not pressed  
        if self.speed > 0:
            self.rotate_car(rotation_speed * 2)
        if self.speed < 0:
            self.speed += self.friction
            self.rotate_car(rotation_speed)

    def check_outofbound_collision(self):
        black = (0,0,0)
        is_on_target,points = collision_check.detect_by_color(self.car_rect,self.image,self.road,self.angle,black)
        if is_on_target:
            power = 500
            collision_points = points
            collision_results = collision_check.push(self.x,self.y,self.angle,self.car_rect,self.velocity,dt,power,collision_points)
            self.x,self.y,self.angle,self.velocity = collision_results

    def check_not_road(self):
        green = (0,255,0)
        is_on_target,points = collision_check.detect_by_color(self.car_rect,self.image,self.road,self.angle,green)
        if is_on_target:
            debug.debug_on_screen(f'not on road','red')
            self.speed = self.velocity.length()
            if self.speed > self.max_speed/3:
                off_road_fiction = self.velocity.normalize()*-self.friction*20
                self.velocity += off_road_fiction *dt

    def logics(self):
        self.check_outofbound_collision()  # collision_check
        self.check_not_road()             # still not finished
        car_sounds.gears()
    def speed_meter(self):
        car_speed = int(self.speed*0.03)
        
        image = self.speed_meter_image
        x = 0 
        y = 0
        rect = image.get_rect(center = (x,y))

        rect.x = 0 #image.get_width()
        rect.y = screen_height - image.get_height() 

        pos = rect.x,rect.y 
        
        speed_num_pos = (rect.centerx-30, rect.centery-30)
        

        font = pg.font.Font(the_font,36)  # (Font name, size)
        speed = font.render(f"{car_speed}", True, (135,206,250))  # White text

        screen.blit(image,(rect.x,rect.y))
        screen.blit(speed, speed_num_pos)

        
    def draw_map(self,camera_x,camera_y):
        screen.blit(self.map, (-camera_x,-camera_y))

    
    

    def draw(self):

        
        camera_x,camera_y =camera(self.x,self.y,screen_size,self.map_size) #sets the camera


        self.draw_map(camera_x,camera_y)

        self.movement()
        self.speed_meter()

        
        car_screen_x = self.x - camera_x
        car_screen_y = self.y - camera_y
        self.car_pos = self.rotated_image.get_rect(center=(car_screen_x,car_screen_y))

       # make_circles(self.car_rect,car_screen_x,car_screen_y,self.angle,self.image)

        screen.blit(self.rotated_image, (self.car_pos)) #car position

        
def make_circles(rect,camera_x,camera_y,angle,original_image):

    points = get_around_points(rect,angle,original_image)

    for point in points:
        # Create a new tuple with the adjusted values
        adjusted_point = (point[0] + camera_x - rect.centerx, point[1] + camera_y - rect.centery)
        
        # Draw the circle using the adjusted point
        pg.draw.circle(screen, (255, 0, 0), adjusted_point, 7)


player_car = Car(**garage[selected_car])


class Car_sounds:
    def __init__(self):
        # Dedicated channels
        self.channel_accel = pg.mixer.Channel(0)
        self.channel_gear = pg.mixer.Channel(1)
        self.channel_loop = pg.mixer.Channel(2)

        self.channel_accel_loop = pg.mixer.Channel(3)

        self.channel_accel.set_volume(0.3)
        self.channel_accel_loop.set_volume(0.3)
        self.channel_loop.set_volume(0.3)
   
        # Dictionary for storing sounds and their "played" states
        self.sounds = {
            'acceleration_1': {'sound': pg.mixer.Sound('sounds/car_acceleration_1.ogg'), 'played': False},
            'acceleration_2': {'sound': pg.mixer.Sound('sounds/car_acceleration_4.ogg'), 'played': False},
            'acceleration_3': {'sound': pg.mixer.Sound('sounds/car_acceleration_3.ogg'), 'played': False},
            'acceleration_4': {'sound': pg.mixer.Sound('sounds/car_acceleration_4.ogg'), 'played': False},
            'gear_1': {'sound': pg.mixer.Sound('sounds/gear_1.ogg'), 'played': False},
            'gear_2': {'sound': pg.mixer.Sound('sounds/gear_2.ogg'), 'played': False},
            'gear_3': {'sound': pg.mixer.Sound('sounds/gear_3.ogg'), 'played': False},
            'gear_4': {'sound': pg.mixer.Sound('sounds/gear_4.ogg'), 'played': False},
            'car_moving_loop': {'sound': pg.mixer.Sound('sounds/car_moving_loop.ogg'), 'played': False}
        }

        self.loops = {
            'loop_1': {'sound':pg.mixer.Sound('sounds/car_acceleration_1_loop.ogg'), 'played': False},
            'loop_2': {'sound':pg.mixer.Sound('sounds/car_acceleration_2_loop.ogg'), 'played': False},
            'loop_3': {'sound':pg.mixer.Sound('sounds/car_acceleration_3_loop.ogg'), 'played': False},
            'loop_4': {'sound':pg.mixer.Sound('sounds/car_acceleration_4_loop.ogg'), 'played': False},
        }

        self.speed = 0

        self.max_speed = int(player_car.max_speed*0.03)



        self.gear_1_limit = self.max_speed/4        
        self.gear_2_limit = self.max_speed/3
        self.gear_3_limit = self.max_speed/2
        self.gear_4_limit = self.max_speed/1.5

        self.gear = 0
        self.old_gear = None
    def car_sound_sys(self):
        self.speed_convert_modifer = 0.03
        self.speed = int(player_car.velocity.length() * self.speed_convert_modifer)

        self.reset_flags_based_on_speed() 
        #self.reset_flags() 
        ## ok the logic is this
        # first accel is turned on meaning true
        # if gear is not shifted let is stay true
        # when that gear is shifted make that accel false
        # and stop that accel and loop 


        # Dynamic gear limits based on acceleration

        

        #debug.debug_on_screen(f'the gear_limites: {self.gear_1_limit,self.gear_2_limit,self.gear_3_limit,self.gear_4_limit}','red')

       # self.gears()
        
        if self.speed < self.gear_1_limit and not self.sounds['acceleration_1']['played']:     ## the acceleration_1
            
            self.channel_loop.stop()
            self.channel_accel.play(self.sounds['acceleration_1']['sound'])
            self.sounds['acceleration_1']['played'] = True
            self.sounds['acceleration_2']['played'] = False

        if self.speed < self.gear_1_limit and self.sounds['acceleration_1']['played']:          ## the loop_2
            if not self.loops['loop_1']['played'] and not self.channel_accel.get_busy():
                self.channel_accel_loop.play(self.loops['loop_1']['sound'],loops=-1)
                self.loops['loop_1']['played'] = True

       
        if self.speed > self.gear_1_limit and not self.sounds['acceleration_2']['played']:  # THE ACCELERATION_2

            self.channel_accel.stop()
            self.channel_loop.stop()
            self.channel_accel.play(self.sounds['acceleration_2']['sound'],)
            self.sounds['acceleration_2']['played'] = True

        if self.speed < self.gear_2_limit and self.sounds['acceleration_2']['played']:    # THE LOOP_2
            if not self.loops['loop_2']['played'] and not self.channel_accel.get_busy():
                self.channel_accel_loop.play(self.loops['loop_2']['sound'],loops=-1)
                self.loops['loop_2']['played'] = True

            
        

        if self.speed > self.gear_2_limit and not self.sounds['acceleration_3']['played']:  # THE ACCELERATION_3

            self.channel_accel.stop()
            self.channel_loop.stop()

            self.channel_accel.play(self.sounds['acceleration_3']['sound'])
            self.sounds['acceleration_3']['played'] = True
            self.loops['loop_3']['played'] = False

        if self.speed < self.gear_3_limit and self.sounds['acceleration_3']['played']:    # THE LOOP_3
            if not self.loops['loop_3']['played'] and not self.channel_accel.get_busy():
                self.channel_accel_loop.play(self.loops['loop_3']['sound'],loops=-1)
                self.loops['loop_3']['played'] = True

            

        if self.speed > self.gear_3_limit and not self.sounds['acceleration_4']['played']:  # THE ACCELERATION_4

            self.channel_accel.stop()
            self.channel_loop.stop()

            self.channel_accel.play(self.sounds['acceleration_4']['sound'],)
            self.sounds['acceleration_4']['played'] = True

        if self.speed < self.gear_4_limit and self.sounds['acceleration_4']['played']:    # THE LOOP_4
            if not self.loops['loop_4']['played'] and not self.channel_accel.get_busy():
                self.channel_accel_loop.play(self.loops['loop_4']['sound'],loops=-1)
                self.loops['loop_4']['played'] = True


        if self.speed > self.gear_4_limit and not self.sounds['car_moving_loop']['played']:    #the infinite LOOOP
            self.channel_accel.stop()
      
            self.channel_loop.play(self.sounds['car_moving_loop']['sound'], loops=-1)
            self.sounds['car_moving_loop']['played'] = True
            self.sounds['gear_4']['played'] = False

        
            
       
    def gears(self):

        buffer_zone_num = 3
        
        buffer_zone_1 = self.gear_1_limit + buffer_zone_num
        buffer_zone_2 = self.gear_2_limit + buffer_zone_num
        buffer_zone_3 = self.gear_3_limit + buffer_zone_num
        buffer_zone_4 = self.gear_4_limit + buffer_zone_num

        #debug.debug_on_screen(f'the current gear:{self.gear}','green')
       # debug.debug_on_screen(f' the previous gear:{self.old_gear}','red')


        if self.speed > self.gear_1_limit and self.speed < buffer_zone_1  and not self.sounds['gear_1']['played'] and self.old_gear != 1:      ## the shift_1
            
            #self.gear = 1
            #self.old_gear = self.gear
            self.set_gear(1)


            self.channel_accel.stop()
            self.channel_accel_loop.stop()
              # makes the first acceleration played false
            self.channel_gear.play(self.sounds['gear_1']['sound'])

            self.sounds['acceleration_1']['played'] = False
            self.sounds['gear_1']['played'] = True
            self.sounds['gear_2']['played'] = False
            self.sounds['acceleration_1']['played'] = False
            self.loops['loop_2']['played'] = False


        elif self.speed > self.gear_2_limit  and self.speed < buffer_zone_2 and not self.sounds['gear_2']['played'] and self.old_gear != 2:         # THE SHIFT_2

            self.set_gear(2)

            self.channel_accel.stop()
            self.channel_accel_loop.stop()
            self.channel_gear.play(self.sounds['gear_2']['sound'])
            self.sounds['gear_2']['played'] = True
            self.sounds['gear_1']['played'] = False
            self.sounds['acceleration_2']['played'] = False
            self.loops['loop_3']['played'] = False
        
        

        elif self.speed > self.gear_3_limit and self.speed < buffer_zone_3 and not self.sounds['gear_3']['played'] and self.old_gear != 3:         # THE SHIFT_3
            #self.gear = 3
            self.set_gear(3)
            self.channel_accel.stop()
            self.channel_accel_loop.stop()   
            self.channel_gear.play(self.sounds['gear_3']['sound'])

            self.sounds['gear_3']['played'] = True
            self.sounds['gear_2']['played'] = False
            self.sounds['acceleration_3']['played'] = False
            self.loops['loop_4']['played'] = False
            
        elif self.speed > self.gear_4_limit and self.speed < buffer_zone_4 and not self.sounds['gear_4']['played'] and self.old_gear != 4:         # THE SHIFT_4  -- last one
           
            
            #self.gear = 4
            self.set_gear(4)
            self.channel_accel.stop()
            self.channel_accel_loop.stop()

            self.channel_gear.play(self.sounds['gear_4']['sound'])

            self.sounds['gear_4']['played'] = True
            self.sounds['gear_3']['played'] = False
            #self.sounds['acceleration_4']['played'] = False



    def reset_keys(self, *keys):
        for k in keys:
            if k in self.sounds:
                self.sounds[k]['played'] = False
            if k in self.loops:
                self.loops[k]['played'] = False


    def reset_flags_based_on_speed(self):
        s = self.speed

        if s < self.gear_1_limit:
            self.reset_keys(
                'loop_2', 'loop_3', 'loop_4',
                'gear_1', 'gear_2', 'gear_3', 'gear_4',
                'car_moving_loop'
            )

        elif s < self.gear_2_limit:
            self.reset_keys(
                
                'loop_3', 'loop_4',
                'gear_2', 'gear_3', 'gear_4',
                'car_moving_loop'
            )

        elif s < self.gear_3_limit:
            self.reset_keys(
                
                'loop_4',
                'gear_3', 'gear_4',
                'car_moving_loop'
            )

        elif s < self.gear_4_limit:
            self.reset_keys(
                'gear_4',
                'car_moving_loop'
            )


    def set_gear(self,gear):
        if self.gear != gear:
            self.gear = gear
            self.lower_speed()
            self.old_gear = gear
            

    def lower_speed(self):
        
        speed_modifer = -10
        
        # speed_penalties = { 
        #     1: (self.gear_1_limit + speed_modifer) / self.speed_convert_modifer,                    #sys type 1
        #     2: ((self.gear_2_limit + self.gear_1_limit) / 2) / self.speed_convert_modifer, 
        #     3: ((self.gear_3_limit + self.gear_2_limit) / 2) / self.speed_convert_modifer, 
        #     4: ((self.gear_4_limit + self.gear_3_limit) / 2) / self.speed_convert_modifer, 
        # }

        speed_penalties = { 
            1: (self.gear_1_limit + speed_modifer) / self.speed_convert_modifer,                #sys type 2
            2: ((self.gear_1_limit + 4)) / self.speed_convert_modifer, 
            3: ((self.gear_2_limit + 4)) / self.speed_convert_modifer, 
            4: ((self.gear_3_limit + 4)) / self.speed_convert_modifer, 
        }


        car_speed = player_car.velocity.length()

        if self.gear in speed_penalties:
            car_speed = player_car.velocity.length()
            lower_amount = speed_penalties[self.gear]

            #new_speed = car_speed - lower_amount
            new_speed =   lower_amount
            player_car.velocity.scale_to_length(new_speed)
           ## the speed loss is too marginal, but if it gets too much than the gear shifts two times, maybe flag system would be good, but too much work



       # print(f'speed_change_to : {lower_amount*0.03} from {getattr(self, f"gear_{self.gear}_limit")}')
        
car_sounds = Car_sounds()

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



pg.quit()
sys.exit()



# TO DO 
 #--GEAR-based sound system for the car
   # the sound will play based on the gear number
   # the gear will change based on the speed
   # need 4 gear changed sound and 4 between the car moving sound
   # the car moving but not accelerating sound will play when w is not pressed
   # the gear will change based on the SPEED 
   # it should work IT MUST WORK :|
   # Update: IT WORKS
## TO DO
# FUCK THIS
#// fix the sound loops

## the sounds are good now
#// FIX THE FUCKING sound resets
## //FIX the sounds when it gets decreased from environments
# FUCK THE SySTEM
  #//THE COLLISION DETECTION IS NOT WORKING CORRECTLY
  #//THE COLLISION SYSTEM PUSH IS FUCKED - fix it
  #///??2 THE COLLISION SYSTEM IS STILL FUCKED, but less, fix it 
  #collision system is now fixed, 
  #collision system improvement,
    #change the angle of the car when it hits the roads edge
    #using vector to decide the angle,
    #the angle should be based on the collision point
      #example: front or back point means t the rotation force = 360 or 0 meaning no angle change
    ##?// close to finishing the direction change based on collision 
    #? better than before but not the best, work on it later