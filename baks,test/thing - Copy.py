import pygame as pg
import time 
import sys
import math
import cv2
import numpy as np
import gc
from PIL import Image

from pprint import pprint

from factory import garage,maps
from kill_bug import debug
from camera import camera
from get_offset_for_mask import get_offset
from collision_detection import collision_check,get_around_points
from menu import Menu
from loader import run_menu
from nitro_parts import nitro
from countdown import Timer
from screen_shaker import screen_shake
from loader import dataloader
from animation_manager import make_animation
from soundsystem import SoundManager
from banksystem import make_bank,bank

pg.init()
pg.mixer.init()
pg.mixer.set_reserved(7)
#debug


#the screen things
clock = pg.time.Clock()
screen_width,screen_height = 1920,1000
screen_size = screen_width,screen_height
screen = pg.display.set_mode((screen_width,screen_height),vsync=1)

make_bank(screen)
selected_car,selected_map =  None,None
game_stat = 'menu'

car_list = list(garage.keys())
map_list = list(maps.keys())
selected_car_number = car_list.index(dataloader.get_car())
selected_map_number = map_list.index(dataloader.get_map())
menu = Menu(screen,screen_size,selected_car_number,selected_map_number)

def goto_menu():
    game_data = run_menu(screen,menu)
    return game_data[0], game_data[1]

game_data = run_menu(screen,menu)#**??** SELECTING THE CAR FROM THE MENU, THIS RUNS THE MENU *???***

race_time = 15

main_soundmanager = SoundManager('sounds')
if game_data == (None,None):
    pg.quit()
    exit()
    
selected_car = game_data[0]
selected_map = game_data[1]

game_stat = 'race' 
timer = Timer(race_time)




pg.display.set_caption('racing')


camera_x,camera_y = 0,0


the_loading_screen_img = pg.image.load('menu_assets/background.jpeg').convert()
the_loading_screen_img = pg.transform.scale(the_loading_screen_img,(screen_size))

def loading_screen():
    screen.blit(the_loading_screen_img,(0,0))
    pg.display.update()

loading_screen()

def loading_bar(w_now=0,color = 'red'):
    w,h = 700,50
    out_ln_w,out_ln_h = 20,20

    x = screen_width/2 - (w+out_ln_w)/2
    y = screen_height - screen_height/4
    

    pg.draw.rect(screen,(0,0,0),(x-10,y-10,w+out_ln_w,h+out_ln_h))  #*outline

    if color == 'blue':
        rgb = (0,0,255)
    elif color == 'green':
        rgb = (0,255,0)
    elif color == 'red':
        rgb = (255,0,0)
    
    w_now = w * (w_now/100)

    pg.draw.rect(screen,rgb,(x,y,w_now,h))
    pg.display.update()

loading_bar(25)

speed_convert_modifer = 0.03

#selected_car = 'BMW' 
the_font = 'Dragrace.ttf'
#glinton
#lamborghini
#esquire
#aston_martin
#pony
#BMW

#selected_map = 'new_loop'
#test
#loop
#river
#city #not good
#village
#high_way 
#new_loop
#elemental




##IMPORTED FUNCT


def check_zoom(raw_map):
    map_width = raw_map.get_width()
    map_height = raw_map.get_height()

    # Reference map stats
    ref_width = 1914
    ref_height = 935
    ref_zoom = 16
    # Calculate average sizes
    ref_avg = (ref_width + ref_height) / 2
    map_avg = (map_width + map_height) / 2
    
    
    # Calculate scale ratio
    scale_ratio = ref_avg / map_avg

    # Final zoom
    zoom =  (scale_ratio)*ref_zoom
    return zoom

def alot_of_images(file_name,file_path,files_num,extension = 'png',size=(100,100)):
    images = []
    for i in range(files_num):
        the_file = f'{file_path}/{file_name}_{i+1}.{extension}'
        image = pg.image.load(the_file)
        image = pg.transform.scale(image,(size))
        images.append(image)
    return images

loading_bar(33)




class Car():
    def __init__(self,width,height,image,acceleration,max_speed,brake,handling,price):
        global dt,selected_map

        self.width = width
        self.height = height
        self.image = image
        self.image = pg.image.load(self.image).convert_alpha()
        self.image = pg.transform.smoothscale(self.image, (self.width,self.height))
        self.car_mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

       

        
        self.original_acceleration = acceleration
        self.acceleration =  acceleration
        self.friction = 500
        self.speed = 0
        self.direction = 0
        self.max_speed = max_speed
        self.base_max_speed = max_speed
        self.brake = brake
        self.rotation_speed = handling

        self.rotated_image = self.image
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
        self.angle = 0

        self.raw_map = pg.image.load(maps[selected_map]['map']).convert()
        self.raw_road_image = pg.image.load(maps[selected_map]['road']).convert()
        self.zoom = check_zoom(self.raw_map)

        self.road_image = pg.transform.scale(self.raw_road_image, (int(self.raw_road_image.get_width()*self.zoom), int(self.raw_road_image.get_height()*self.zoom)))
        self.road = self.road_image
        
        del self.raw_road_image
        
        self.map = pg.transform.scale(self.raw_map, (int(self.raw_map.get_width()*self.zoom), int(self.raw_map.get_height()*self.zoom)))
        #self.map = self.road
        self.map_size = self.map.get_width(),self.map.get_height()

        del self.raw_map
        self.x,self.y = self.find_Spawn()
        self.x *= self.zoom
        self.y *= self.zoom

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
        
        self.nitro_on = False

        self.explosion_images = alot_of_images('explosion','car_assets/explosion', 7, 'PNG')
        self.dead = False
        self.cheat_death = False
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
        speed_loss_start_speed = self.base_max_speed/2
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
        self.angle %= 360


    def screen_collision_check(self,vector,car_rect):
        screen_rect = screen.get_rect()

        if not screen.get_rect().contains(car_rect):
            # Car is touching or outside the screen edges
            collision_results = collision_check.push(self.x, self.y,self.angle,self.velocity.x, self.velocity.y, vector, dt, 500)
            self.x = collision_results[0]
            self.y = collision_results[1]
            self.velocity.x = collision_results[3]
            self.velocity.y = collision_results[4]

    def nitro(self,forward,nitro_power:int,):
        if not nitro.is_active and not nitro.nitro_cheat_on:
            main_soundmanager.reset_flag(True)
            return
        current_frame = nitro.give_nitro()
        current_frame = pg.transform.flip(current_frame,True,False)

        pos,image = get_wheel_pos_and_angle_for_image(current_frame)
        image2 = image

        camera_pos = pg.Vector2(camera_x,camera_y)
        screen_pos_1 = pos[0] - camera_pos
        screen_pos_2 = pos[1] - camera_pos

        rect_1 = image.get_rect(center=screen_pos_1)
        rect_2 = image2.get_rect(center=screen_pos_2)

        screen.blit(image,rect_1)
        screen.blit(image2,rect_2)

        self.velocity += forward*nitro_power*dt

        main_soundmanager.play('nitro_use',loop=False,volume=1,extension='mp3')
        for sound_data in car_sounds.sounds.values():
            sound_data['sound'].set_volume(1.0)

        for loop_data in car_sounds.loops.values():
            loop_data['sound'].set_volume(1.0)

        # Also set channel volumes
        #car_sounds.channel_accel.set_volume(1.0)
        car_sounds.channel_accel_loop.set_volume(1.0)
        car_sounds.channel_loop.set_volume(1.0)

    def movement(self):
        
        rotation_speed = self.rotation_speed
        #new_speed = self.max_speed
        self.keys = pg.key.get_pressed()

        #self.new_drift = 0      

        rad = math.radians(self.angle)
    
        dx = math.cos(rad)
        dy = -math.sin(rad)

        forward = pg.Vector2(dx,dy)
        
       # is_on_color = self.is_on()
        #debug.debug_on_screen(f'is on: {is_on_color}', 'blue')
        thing1,thing2 =  car_sounds.channel_accel_loop.get_volume(),car_sounds.channel_accel_loop.get_volume()

        if self.keys[pg.K_SPACE]:
            if self.speed*speed_convert_modifer > 1:

                car_sounds.hand_brake()
                tire_marks.tire_mark_on = True

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
            car_sounds.channel_hand_brake.stop()
            car_sounds.hand_brake_sound['hand_brake']['played'] = False
            tire_marks.tire_mark_on = False
                  # recover grip gradually
                
           
        
        
        
        multiplyer = 5
        if timer.start_race_time(screen):
            if self.keys[pg.K_LSHIFT]:
                
                if not self.nitro_on:
                    self.max_speed *= multiplyer
                    self.nitro_on = True
                    
                if self.velocity.length() >0:
                    nitro_power = 1000
                    screen_shake.apply_shake(1,1)
                    self.nitro(forward,nitro_power)
                if not nitro.is_active:
                    self.max_speed = self.base_max_speed
            elif self.nitro_on:
                self.max_speed = self.base_max_speed
        
                nitro.reset()
                main_soundmanager.reset_flag(True)
                car_sounds.nitro_reset_sound()
                self.nitro_on = False

            if self.keys[pg.K_w]:
                speed_by_direction = self.velocity.dot(forward)
                car_sounds.car_accelerating = True
                self.velocity += self.acceleration * dt*forward
                car_sounds.car_sound_sys()
                
                if self.speed < 0:
                    self.speed += (5*self.acceleration) *dt
                if speed_by_direction < 0:
                    tire_marks.tire_mark_on = True
                else:
                    if not self.keys[pg.K_SPACE]:
                        tire_marks.tire_mark_on = False

                self.rotate_car(rotation_speed)


                

            elif self.keys[pg.K_s]:
                speed_by_direction = self.velocity.dot(forward)
                car_sounds.brake(speed_by_direction)
                reverse_speed = -self.max_speed/4
                if speed_by_direction > reverse_speed:
                    self.velocity -= self.brake*forward
                if self.speed > self.max_speed/2:
                    self.rotate_car(rotation_speed * 1.4)
                self.rotate_car(rotation_speed)
                if speed_by_direction > 0:
                    tire_marks.tire_mark_on = True
                else:
                    tire_marks.tire_marks_on = False
        
            
            

            else:
                self.not_accelerating(rotation_speed)
            
        
        #* Previous acceleration modifer
        # if self.acceleration > 0:
        #     if self.speed >= self.max_speed and self.nitro_on:
        #         self.acceleration = 0  # Hard stop at max speed
        #     elif not self.nitro_on and self.speed <= self.max_speed:
        #         acceleration_modifer = (self.speed/self.max_speed)*self.original_acceleration
        #         self.acceleration = self.original_acceleration - acceleration_modifer

        #debug.debug_on_screen(self.acceleration,'green')

        

        #*better version
        acceleration_modifer = (self.speed/self.max_speed)*self.original_acceleration
        self.acceleration = self.original_acceleration - acceleration_modifer


        self.velocity = (self.drift(forward,self.velocity,(self.drift_factor*self.new_drift)))
        
         
        
        steps = min(int(self.velocity.length() * dt // 10) + 1, 50)  # 10 px per substep (adjustable)
        self.rotated_image = pg.transform.rotozoom(self.image,self.angle,1.0)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))
        self.car_image = self.rotated_image  # the masks
        self.car_rect = self.rect
        for _ in range(steps):
            self.x += self.velocity.x * dt / steps
            self.y += self.velocity.y * dt / steps


            self.rect.center = (self.x, self.y)
            self.rect.clamp_ip(self.map.get_rect())
            self.x, self.y = self.rect.center
            
            self.check_outofbound_collision()
            #check_points.check_colors()
    
        self.logics()

          # gradual reduction




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


        for sounds in car_sounds.loops:
            car_sounds.loops[sounds]['played'] = False            
        
        for gear in ['gear_1', 'gear_2', 'gear_3', 'gear_4']:
            car_sounds.sounds[gear]['played'] = False
        
        
        for sounds in car_sounds.sounds:
            car_sounds.sounds[sounds]['played'] = False

        car_sounds.sounds['brake_loop']['played'] = False

        car_sounds.channel_brake_loop.stop()
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
            #debug.debug_on_screen(f'not on road','red')
            self.speed = self.velocity.length()
            if self.speed > self.max_speed/3:
                off_road_fiction = self.velocity.normalize()*-self.friction*20
                self.velocity += off_road_fiction *dt

    def logics(self):
        #self.check_not_road()             # still not finished
        nitro.nitro_bar(screen,self.nitro_on)
        self.dead = self.death()

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
        speed = font.render(f"{car_speed}", True, (135,206,250))  # blueis text

        screen.blit(image,(rect.x,rect.y))
        screen.blit(speed, speed_num_pos)
    
    def death(self):
        if self.cheat_death:
            return

        if timer.time_left < 0:            
            frame = make_animation.get_frame(self.explosion_images, one_loop=True)

            main_soundmanager.play('ground_explosion')
            self.rotated_image = frame
            
            if not pg.surfarray.pixels_alpha(frame).any():
                
                make_animation.reset()
                return True

    def draw(self):

        global camera_x,camera_y
        camera_x,camera_y =camera(self.x,self.y,screen_size,self.map_size) #sets the camera
        

        self.speed_meter()

    
        car_screen_x = self.x - camera_x
        car_screen_y = self.y - camera_y
        self.car_pos = self.rotated_image.get_rect(center=(car_screen_x,car_screen_y))


        screen.blit(self.rotated_image, (self.car_pos)) #car position
        if not self.dead:
            self.movement()
        else:
            race_end()
        #make_circles(self.car_rect,car_screen_x,car_screen_y,self.angle,self.image)

loading_bar(50) #* LOADING 50% DONE
timer = Timer(race_time)

def get_wheel_pos_and_angle_for_image(the_image):
    image = the_image
    car_image = player_car.image
    angle = player_car.angle

    rotated_image = pg.transform.rotate(the_image,angle)

    half_width = car_image.get_width()//2
    half_height = car_image.get_height()//2

    offsets = [
        pg.Vector2(-half_width,-half_height),  #rightwheel
        pg.Vector2(-half_width,half_height)    #leftwheel
    ]
    wheel_positions = []
    car_center = pg.Vector2(player_car.x, player_car.y)
    for offset in offsets:
        rotated_offset = offset.rotate(-angle)
        wheel_pos = rotated_offset + car_center
        wheel_positions.append(wheel_pos)

    return wheel_positions,rotated_image



def make_circles(rect,camera_x,camera_y,angle,original_image):

    points = get_around_points(rect,angle,original_image)

    for point in points:
        # Create a new tuple with the adjusted values
        adjusted_point = (point[0] + camera_x - rect.centerx, point[1] + camera_y - rect.centery)
        
        # Draw the circle using the adjusted point
        pg.draw.circle(screen, (255, 0, 0), adjusted_point, 7)



player_car = Car(**garage[selected_car])







class Tire_marks:
    def __init__(self):
        self.life = 255
        self.tire_mark_image = pg.image.load('car_assets/tire_mark.png').convert_alpha()
        self.tire_mark_width,self.tire_mark_height = 20,10
        self.tire_mark_image = pg.transform.scale(self.tire_mark_image,(self.tire_mark_width,self.tire_mark_height))
        self.tire_mark_image.set_alpha(self.life)
        self.tire_mark_on = False
        self.tire_marks = []
        self.last_mark_time = 0
        self.mark_interval = 0

        self.tire_gride_pos = set()
    def show_tire_mark(self):

        if not self.tire_mark_on:
            return
        self.last_mark_time += dt
        if self.last_mark_time < self.mark_interval:
            return
        self.last_mark_time = 0

        image = self.tire_mark_image
        car_image = player_car.image
        angle = player_car.angle

        rotated_mark = pg.transform.rotate(image,angle)

        half_width = car_image.get_width()//2
        half_height = car_image.get_height()//2

        offsets = [
            pg.Vector2(-half_width,-half_height),  #rightwheel
            pg.Vector2(-half_width,half_height)    #leftwheel
        ]

        car_center = pg.Vector2(player_car.x, player_car.y)
        for offset in offsets:
            rotated_offset = offset.rotate(-angle)
            wheel_pos = rotated_offset + car_center  
           

            grid_pos = int(wheel_pos.x//5),int(wheel_pos.y//5)

            if grid_pos not in self.tire_gride_pos:
                self.tire_gride_pos.add(grid_pos)
                tire_marks_data = {
                    'image': rotated_mark,
                    'pos': wheel_pos,
                    'opacity': 255,
                    'grid_pos': grid_pos
                }
                self.tire_marks.append(tire_marks_data)
    def update_tire_marks(self):
        if self.tire_mark_on or not self.tire_mark_on:
            for tire_mark in self.tire_marks[:]:
                tire_mark['opacity'] -= 1
                
                if tire_mark['opacity'] <= 0:
                    self.tire_gride_pos.discard(tire_mark['grid_pos'])
                    self.tire_marks.remove(tire_mark)
                    continue
                tire_mark['image'].set_alpha(tire_mark['opacity'])



          
    def make(self):
        camera_offset = pg.Vector2(camera_x,camera_y)
      #  debug.debug_on_screen(len(self.tire_marks))
        for tire_mark in self.tire_marks:
            screen_pos = tire_mark['pos'] - camera_offset
            rect = tire_mark['image'].get_rect(center=screen_pos)
            if not screen.get_rect().contains(rect):
                self.tire_marks.remove(tire_mark)
                self.tire_gride_pos.discard(tire_mark['grid_pos'])
            screen.blit(tire_mark['image'],rect)
    
tire_marks = Tire_marks()
loading_bar(70) #? LOADING 70% DONE

class Car_sounds:
    def __init__(self):
        # Dedicated channels
        self.channel_accel = pg.mixer.Channel(0)
        self.channel_gear = pg.mixer.Channel(1)
        self.channel_loop = pg.mixer.Channel(2)
        self.channel_accel_loop = pg.mixer.Channel(3)
        self.channel_brake_loop = pg.mixer.Channel(4)
        self.channel_hand_brake = pg.mixer.Channel(5)

        self.volume = 0.7
        self.channel_accel.set_volume(self.volume)
        self.channel_accel_loop.set_volume(self.volume)
        self.channel_loop.set_volume(self.volume)
        self.channel_hand_brake.set_volume(self.volume)
   

        self.sounds = {
            'acceleration_1': {'sound': pg.mixer.Sound('sounds/car_acceleration_1.ogg'), 'played': False},
            'acceleration_2': {'sound': pg.mixer.Sound('sounds/car_acceleration_4.ogg'), 'played': False},
            'acceleration_3': {'sound': pg.mixer.Sound('sounds/car_acceleration_3.ogg'), 'played': False},
            'acceleration_4': {'sound': pg.mixer.Sound('sounds/car_acceleration_4.ogg'), 'played': False},
            'gear_1': {'sound': pg.mixer.Sound('sounds/gear_1.ogg'), 'played': False},
            'gear_2': {'sound': pg.mixer.Sound('sounds/gear_2.ogg'), 'played': False},
            'gear_3': {'sound': pg.mixer.Sound('sounds/gear_3.ogg'), 'played': False},
            'gear_4': {'sound': pg.mixer.Sound('sounds/gear_4.ogg'), 'played': False},
            'car_moving_loop': {'sound': pg.mixer.Sound('sounds/car_moving_loop.ogg'), 'played': False},
            'brake_loop': {'sound': pg.mixer.Sound('sounds/brake_loop.ogg'),'played': False},
        }

        self.hand_brake_sound = {'hand_brake': {'sound': pg.mixer.Sound('sounds/hand_brake.wav'),'played':False}}



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

    def hand_brake(self):
        if not self.hand_brake_sound['hand_brake']['played']:
            self.channel_hand_brake.play(self.hand_brake_sound['hand_brake']['sound'],loops =- 1)
            self.hand_brake_sound['hand_brake']['played'] = True
            
       
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


    def brake(self,speed_by_direction):
        if not self.sounds['brake_loop']['played'] and speed_by_direction > 0:
            
            self.channel_accel.stop()
            self.channel_accel_loop.stop()
            self.channel_brake_loop.play(self.sounds['brake_loop']['sound'])
            self.sounds['brake_loop']['played'] = True
        elif  speed_by_direction < 0:
            self.channel_brake_loop.stop()
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
    def stop_all(self):
        self.channel_accel.stop()
        self.channel_accel_loop.stop()
        self.channel_brake_loop.stop()
        self.channel_gear.stop()
        self.channel_loop.stop()
        self.channel_hand_brake.stop()        

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

    def nitro_reset_sound(self):
        self.channel_accel.set_volume(self.volume)
        self.channel_accel_loop.set_volume(self.volume)
        for sound_data in car_sounds.sounds.values():
            sound_data['sound'].set_volume(self.volume)

        for loop_data in car_sounds.loops.values():
            loop_data['sound'].set_volume(self.volume)
    
       # print(f'speed_change_to : {lower_amount*0.03} from {getattr(self, f"gear_{self.gear}_limit")}')
        
car_sounds = Car_sounds()




the_map = player_car.map


def draw_map(camera_x,camera_y):

        offset_x,offset_y = screen_shake.make()
        screen.blit(the_map, (-camera_x+offset_x,-camera_y+offset_y))

class Check_points:
    def __init__(self):
        self.colors_to_check = {
            'color_1': {
                'color': (0,0,254),
                'check': False,
                'added_time': False
            },
            'color_2': {
                'color': (0,0,253),
                'check': False,
                'added_time': False
            },
            'color_3': {
                'color': (0,0,252),
                'check': False,
                'added_time': False,
            },
            'color_4': {
                'color': (0,0,251),
                'check': False,
                'added_time': False,
            },
            'color_5': {
                'color': (0,0,250),
                'check': False,
                'added_time': False,
            },
            'color_6': {
                'color': (0,0,249),
                'check': False,
                'added_time': False,
            },
            'color_7': {
                'color': (0,0,248),
                'check': False,
                'added_time': False,
            },
            'color_8': {
                'color': (0,0,247),
                'check': False,
                'added_time': False,
            },
        
            'color_9': {
                'color': (0,0,246),
                'check': False,
                'added_time': False,
            },
            'color_10': {
                'color': (0,0,255),
                'check': False,
                'added_time': False,
            },
        }
        
        self.image = player_car.image
        self.road = player_car.road
        
    def is_on(self):

        x = max(0, min(int(self.car_x), self.road.get_width()-1))
        y = max(0, min(int(self.car_y), self.road.get_height()-1))

        self.pixel_color = self.road.get_at((int(x),int(y)))
        
        return self.pixel_color[:3]

    def check_colors(self):
        self.angle = player_car.angle
        self.car_rect = player_car.car_rect
        self.car_x,self.car_y = player_car.x,player_car.y
        #color = self.is_on()

        steps = min(int(player_car.velocity.length()*dt//10) + 1,50)

        for _ in range (steps):
            self.car_x += player_car.velocity.x*dt / steps
            self.car_y += player_car.velocity.y*dt / steps

            x = max(0, min(int(self.car_x), self.road.get_width()-1))
            y = max(0, min(int(self.car_y), self.road.get_height()-1))

            self.pixel_color = self.road.get_at((int(x),int(y)))
            color = self.is_on()

            for data in self.colors_to_check.values():
                if data['color'] == color:
                    data['check'] = True
                    if not data['added_time']:
                        timer.add_time(10)
                        data['added_time'] = True
                


        #for data in self.colors_to_check.values():
             #debug.debug_on_screen(f'check:{data['check']}', 'blue')

        debug.debug_on_screen(f'on_this_color: {color}', 'yellow')
    def restart(self):
        for values in self.colors_to_check.values():
            values['check'] = False
            values['added_time'] = False

    def conclusion(self):
        self.check_colors()
        if all(v['check'] for v in self.colors_to_check.values()):

            race_end()
            print('GAME WON')

def race_end():
    global game_stat
    #bank.add_money(money_to_add)
    if not player_car.dead:
        menu.reset_spawned_money(timer.time_left)
    game_stat = 'menu'

    

def show_timer():
    pos = screen.get_rect()
    timer.show_time(screen,pos.topright)

check_points = Check_points()



    




def draw_on_game_on():

    tire_marks.make()
    player_car.draw()
    show_timer()
def update_all():
    draw_map(camera_x,camera_y)
    tire_marks.show_tire_mark()
    tire_marks.update_tire_marks()
    pass

def world_logics():
    check_points.conclusion()


loading_bar(100)
running = True
timer = None
timer = Timer(race_time)
while running:
   

    global game_on
    dt = clock.tick(100)/1000
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False



    if game_stat == 'race':
    # Game is active - run game logic
        update_all()
        draw_on_game_on()
        world_logics()
        
        # Check if game should end (all checkpoints completed)
    elif game_stat == "menu":

        #pg.mixer.stop()
        car_sounds.stop_all()
        main_soundmanager.reset_flag()
        player_car = None
        car_sounds = None
        tire_marks = None
        check_points = None
        the_map = None
        timer = None
        menu.game_on = False
        gc.collect()
        
        selected_car, selected_map = goto_menu()
        
        if selected_car is None or selected_map is None:
            running = False
            pg.quit()
            exit()
            
        loading_screen()
        
        loading_bar(50)
        player_car = Car(**garage[selected_car])

        timer = Timer(race_time)
        loading_bar(60)
        car_sounds = Car_sounds()

        loading_bar(70)
        tire_marks = Tire_marks()

        check_points = Check_points()
        loading_bar(100)
        
        the_map = player_car.map
        timer.reset(race_time)
        
        game_stat = "race"

    
        
    debug.show_bug(screen,screen_size)

    pg.display.flip()



pg.quit()
sys.exit()

#Main MENU
#improve visually 
#start with map 
    #add a cool
    #maybe switch to tile_base map ##? NOpe



    #//libpng warning: iCCP: known incorrect sRGB profile FIX THIS
    #// a lot of money spawing at the start after race ends, menu loading time?