import pygame as pg
import time 
import sys
import math
import cv2
import numpy as np
import gc
from mutagen import File as mutafile
from multiprocessing import process
from pprint import pprint
from PIL import Image
import os
import json
from pathlib import Path


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
from SaveFileManager import savemanager
from chunk_map import ChunkMap
pg.init()
pg.mixer.init()
pg.mixer.set_reserved(7)
#debug

#print(f'startup objects: {len(gc.get_objects())}')
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


"""
the timer is cursed and i do not want to fix it by fixing the code, the player gets 5 second less time when starting another race after the first one, 
but time has no problem when its the first time launching the game, so i add 5 second based on the situation,
easy fix, not ideal but works
"""


main_soundmanager = SoundManager('sounds')
race_end_sound_manager = SoundManager('race_end_assets/sounds')
map_sound_manager = SoundManager('map_assets/sounds')
if game_data == (None,None):
    pg.quit()
    exit()
    
selected_car = game_data[0] #returns the names
selected_map = game_data[1]

game_stat = 'race' 

race_time = maps[selected_map]['time']
base_race_time = race_time
first_launch = True

def fix_time_bug():
    global race_time,first_launch
    if first_launch:
        race_time = race_time + 2
        first_launch = False
        #print('first_launch, time not modified')
    else:
        race_time = base_race_time + 5 
        #print('not first launch, time modified by 5')
timer = Timer(race_time)



fix_time_bug()

pg.display.set_caption('racing')


camera_x,camera_y = 0,0


the_loading_screen_img = pg.image.load('menu_assets/background.jpeg').convert()
the_loading_screen_img = pg.transform.scale(the_loading_screen_img,(screen_size))

def loading_screen():
    
    screen.blit(the_loading_screen_img,(0,0))
    pg.display.update()

loading_screen()

def loading_bar(w_now=0,color = 'red'):
    loading_screen()
    w,h = 700,50
    out_ln_w,out_ln_h = 20,20

    x = screen_width/2 - (w+out_ln_w)/2
    y = screen_height - screen_height/4
    

    bar_rect = pg.draw.rect(screen,(0,0,0),(x-10,y-10,w+out_ln_w,h+out_ln_h))  #*outline

    if color == 'blue':
        rgb = (0,0,255)
    elif color == 'green':
        rgb = (0,255,0)
    elif color == 'red':
        rgb = (255,0,0)
    
    w_now = w * (w_now/100)

    pg.draw.rect(screen,rgb,(x,y,w_now,h))
    menu.change_tips()
    
    menu.loading_tips(screen,bar_rect)
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


def check_zoom(w,h):
    map_width = w
    map_height = h

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
    #print(f'the_zoom: {zoom}')
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

        image = maps[selected_map]['road']

        self.img_for_cv2 = cv2.imread(image)
        self.spawn_data = self.find_Spawn()
        self.rotated_image = self.image
        self.rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
        self.angle_coords_x,self.angle_coords_y = self.spawn_data[1]
        
        raw_peek = Image.open(maps[selected_map]['map'])
        raw_w, raw_h = raw_peek.size
        raw_peek.close()
        
        self.zoom = check_zoom(raw_w, raw_h)
        
        self.map = ChunkMap(maps[selected_map]['map'],self.zoom)
        self.raw_map_size = self.map.raw_map_size
        self.map_size = self.map.map_width, self.map.map_height
      
       
        
        self.raw_road_image = pg.image.load(maps[selected_map]['road']).convert()
        self.road_image = pg.transform.scale(self.raw_road_image, (int(self.raw_road_image.get_width()*self.zoom), int(self.raw_road_image.get_height()*self.zoom)))
        self.road = self.road_image
        del self.raw_road_image


        self.x,self.y = self.spawn_data[0]

        self.angle_rad = math.atan2(-(self.angle_coords_y-self.y),(self.angle_coords_x-self.x))
        self.angle = math.degrees(self.angle_rad)
        self.rotated_image = pg.transform.rotate(self.rotated_image,self.angle)
        #print(self.angle)
        #print(f'cyan: {self.angle_coords_x,self.angle_coords_y}, Red: {self.y,self.x}')

        self.x *= self.zoom
        self.y *= self.zoom

        self.camera_x = self.x - screen_width//2
        self.camera_y = self.y - screen_height//2

        self.camera_smooth_motion_x = self.x
        self.camera_smooth_motion_y = self.y

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
        self.death_start_time = None
        self.game_over_screen_alpha_rate = 0
        self.death_to_menu_delay = 7000 #* milliseconds only
    def find_Spawn(self): #//trying the new thing. getting numpy error axis aerror 2 is out of bounds
         # Load image

        im = self.img_for_cv2

        # Define the RED,cyan colour we want to find - remember OpenCV uses BGR ordering
        red = [0,0,255]
        cyan = [255,255,0]

        # Get X and Y coordinates of all red,cyan pixels
        red_Y,red_X = np.where(np.all(im==red,axis=2))
        cyan_Y,cyan_X = np.where(np.all(im==cyan,axis=2))

        if len(red_X) == 0:
            #print("Spawn color not found, brother. Check your logic map.")
            red_Y,red_X = [(0,0),(0,0)]

        if len(cyan_X) == 0:
           # print("Your map does not contain an angle modifier…why?")
            cyan_X,cyan_Y = [(0,0),(0,0)]

        data = [(red_X[0],red_Y[0]),(cyan_X[0],cyan_Y[0])]

        return data

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
        
        is_on_color = self.is_on()
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
        debug.debug_on_screen(f"x,y = {self.x,self.y}",color='red')
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
        global game_stat
        if self.cheat_death:
            return
        if timer.time_left < 0:            
            frame = make_animation.get_frame(self.explosion_images,one_loop=True)

            main_soundmanager.play('ground_explosion')
            car_sounds.stop_all()

            race_end_sound_manager.play('ambulance','mp3')
            game_stat = 'game_over'
            self.rotated_image = frame
            
            if not pg.surfarray.pixels_alpha(frame).any():
                return True

    def player_dead(self):
        global game_stat
        delay = self.death_to_menu_delay
        if self.death_start_time is None:
            self.death_start_time = pg.time.get_ticks()
        if pg.time.get_ticks()-self.death_start_time > delay:
            game_stat = 'menu'

        debug.debug_on_screen(f'{pg.time.get_ticks()-self.death_start_time }',color='red')
        
    
    def get_camera_target(self):
        global camera_x, camera_y

        base_look_further = 100
        changed_base_on_speed = 0.3
        speed = self.velocity.length()
        look_further = speed * changed_base_on_speed

        direction = self.velocity.normalize() if self.velocity.length() != 0 else pg.Vector2(0, 0)
        camera_target_x = self.x + direction.x * look_further
        camera_target_y = self.y + direction.y * look_further
        smooth_factor = 0.2


        camera_x, camera_y = camera(self.camera_smooth_motion_x, self.camera_smooth_motion_y, screen_size, self.map_size)

        car_screen_x = self.x - camera_x
        car_screen_y = self.y - camera_y

    
        half_w, half_h = screen_size[0] / 2, screen_size[1] / 2
        camera_target_x = max(self.x - half_w + 10, min(self.x + half_w - 10, camera_target_x))
        camera_target_y = max(self.y - half_h + 10, min(self.y + half_h - 10, camera_target_y))


        self.camera_smooth_motion_x += (camera_target_x - self.camera_smooth_motion_x) * smooth_factor
        self.camera_smooth_motion_y += (camera_target_y - self.camera_smooth_motion_y) * smooth_factor


        camera_x, camera_y = camera(self.camera_smooth_motion_x, self.camera_smooth_motion_y, screen_size, self.map_size)

        car_screen_x = int(self.x - camera_x)
        car_screen_y = int(self.y - camera_y)
        #debug.debug_on_screen(f'{self.x,self.y}')
        return car_screen_x, car_screen_y


    def draw(self):

        global camera_x,camera_y
        
        car_screen_x,car_screen_y = self.get_camera_target() 
        #camera_x,camera_y =camera(self.camera_smooth_motion_x,self.camera_smooth_motion_y,screen_size,self.map_size) #sets the camera
        

        self.speed_meter()

        
        #car_screen_x = self.x - camera_x 
       # car_screen_y = self.y - camera_y
        self.car_pos = self.rotated_image.get_rect(center=(car_screen_x,car_screen_y))

        
        screen.blit(self.rotated_image, (self.car_pos)) #car position
        if not self.dead:
            self.movement()
        else:
            self.player_dead()
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



class MiniMap:
    def __init__(self,player_car):
        
        self.current_map_index = menu.selected_map_number
        self.current_car_index = menu.selected_car_number
        self.get_map()
        self.get_car()
        self.mini_map_rect = self.mini_map.get_rect()
        self.player_car = player_car
        self.car_image = player_car.image
    def get_map(self):
        self.mini_maps_list = map_list
        self.mini_map_name = map_list[self.current_map_index]
        self.mini_map = maps[self.mini_map_name]['thumbnail']
        self.mini_map = pg.image.load(self.mini_map).convert_alpha()
        self.mini_map = pg.transform.scale(self.mini_map,(300,300))
    def get_car(self):
        car_name = car_list[self.current_car_index]
        the_car =  garage[car_name]['image']
        self.car_image = pg.image.load(the_car).convert_alpha()

    def get_car_info(self):
        car_angle = self.player_car.angle
        car_location = (self.player_car.x,self.player_car.y)
        car_name = car_list[menu.selected_car_number]
        car_image = garage[car_name]['image']

        zoom_level = self.player_car.zoom
        return car_image,car_angle,car_location,zoom_level

    def show_mini_map(self):
        if self.current_map_index != menu.selected_map_number:
            self.current_map_index = menu.selected_map_number
            self.get_map()
        border_color = (0, 0, 0)  # black
        border_thickness = 8
        
        screen_rect = screen.get_rect()
        mini_map_rect = self.mini_map.get_rect(topleft=screen_rect.topleft)
        #car_rect = self.player_car.rotated_image.get_rect(center=(self.player_car.x,self.player_car.y))
        
        #coords convertion
        world_map_size = player_car.raw_map_size #w,h

        car_x,car_y = self.player_car.car_pos.center

        car_rect = self.player_car.rotated_image.get_rect(center=(car_x,car_y))



        if mini_map_rect.colliderect(car_rect):
            self.mini_map.set_alpha(30)
            debug.debug_on_screen('true')
        else:
            self.mini_map.set_alpha(255)

        screen.blit(self.mini_map, mini_map_rect)
        outline = mini_map_rect.inflate(2, 2)
        pg.draw.rect(screen, border_color, outline, border_thickness)
        self.show_car_on_map(mini_map_rect)

    def show_car_on_map(self,map_rect):

        image,angle,location,zoom = self.get_car_info()
        if menu.selected_car_number != self.current_car_index:
            self.get_car()
            self.current_car_index = menu.selected_car_number
        car_image = self.car_image
        car_height = 5
        car_width = car_height*2.6
        car_size = (car_width,car_height)
        car_image = pg.transform.smoothscale(car_image,car_size)
        car_image = pg.transform.rotate(car_image,angle)

        car_x,car_y = location
        world_map_size = player_car.raw_map_size #w,h

        nx = car_x/(zoom*world_map_size[0])
        ny = car_y/(zoom*world_map_size[1])

        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))

        map_x = nx*self.mini_map.get_width()
        map_y = ny*self.mini_map.get_height()

        minimap_car_x = map_rect.x + map_x 
        minimap_car_y = map_rect.y + map_y
        map_loc  = (minimap_car_x,minimap_car_y)
        #debug.debug_on_screen(map_loc)

        car_rect = car_image.get_rect(center=map_loc)
        screen.blit(car_image,car_rect)
        

minimap = MiniMap(player_car)


def draw_map(camera_x, camera_y):
    offset_x, offset_y = screen_shake.make()
    the_map.update(int(camera_x), int(camera_y), screen_width, screen_height)
    the_map.draw(screen, int(camera_x), int(camera_y), offset_x, offset_y)

    

def get_image(name,extension = 'png',size=(100,100)):
    path = f'map_assets/{name}.{extension}'
    image = pg.image.load(path)
    image = pg.transform.scale(image,size)
    return image



class Check_points:
    def __init__(self):
        check_limits = 40
        size = (300,300)
        self.time_adder_image = get_image('time_add',size=size)
        self.colors_to_check = { 
                f'color_{i}': {
                    'color': (0,0,256-i),
                    'check': False,
                    'added_time': False,
                }
                for i in range (1,check_limits)
            }
        self.colors_to_check_for_check_points = {  #*BGR
                f'color_{i}': {
                    'color': (255-i,0,0),
                    'check': False,
                    'added_time': False,
                }
                for i in range (1,check_limits)
            }
        self.race_end_test =False
        # self.colors_to_check = {
        # 'color_1': {
        #     'color': (0,0,254),
        #     'check': False,
        #     'added_time': False

        #     },
        # 'color_2': {
        #     'color': (0,0,253),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_3': {
        #     'color': (0,0,252),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_4': {
        #     'color': (0,0,251),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_5': {
        #     'color': (0,0,250),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_6': {
        #     'color': (0,0,249),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_7': {
        #     'color': (0,0,248),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_8': {
        #     'color': (0,0,247),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_9': {
        #     'color': (0,0,246),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_10': {
        #     'color': (0,0,245),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_11': {
        #     'color': (0,0,244),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_12': {
        #     'color': (0,0,243),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_13': {
        #     'color': (0,0,242),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_14': {
        #     'color': (0,0,241),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_15': {
        #     'color': (0,0,240),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_16': {
        #     'color': (0,0,239),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_17': {
        #     'color': (0,0,238),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_18': {
        #     'color': (0,0,237),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_19': {
        #     'color': (0,0,236),
        #     'check': False,
        #     'added_time': False
        # },
        # 'color_20': {
        #     'color': (0,0,255),
        #     'check': False,
        #     'added_time': False
        # },
        # }
        
        self.image = player_car.image
        self.road = player_car.road

        self.blue_channel  = player_car.img_for_cv2[:, :, 0]
        self.green_channel = player_car.img_for_cv2[:, :, 1]
        self.red_channel   = player_car.img_for_cv2[:, :, 2]
        
        self.colors_found = {}        
        
        current_map_name = map_list[menu.selected_map_number]
        self.color_file = f'temp_files/check_points_dir/{current_map_name}_check_points/{current_map_name}_check_points.json'
        self.color_dict_path = f'temp_files/check_points_dir/{current_map_name}_check_points'
       
        os.makedirs(self.color_dict_path,exist_ok=True)

        self.colors_found = {} 
        
        my_file =  Path(self.color_file)
        
        if not my_file.exists():
            print('does not exist ')

            self.get_points_for_checks()
        else:
            print('it exist')
            with open(self.color_file, "r") as f:
                self.colors_found = json.load(f)
        

        
    def is_on(self):

        x = max(0, min(int(self.car_x), self.road.get_width()-1))
        y = max(0, min(int(self.car_y), self.road.get_height()-1))

        self.pixel_color = self.road.get_at((int(x),int(y)))
        
        return self.pixel_color[:3]
    def get_points_for_checks(self):
        colors_to_check = self.colors_to_check_for_check_points
        im = player_car.img_for_cv2
        for color_id,data in colors_to_check.items():
            color = np.array(data['color'])
            mask = (self.blue_channel == color[0]) & (self.green_channel == color[1]) & (self.red_channel == color[2])
            mask2 = self.blue_channel == data['color'][0]

            color_y, color_x = np.where(mask)



            # try:    
            #     color_x_mid = sum(color_x)/len(color_x)
            #     color_y_mid = sum(color_y)/len(color_y)
            # except ZeroDivisionError:
            #     return
            if len(color_x) == 0 or len(color_y) == 0: 
                continue
            
            
            self.colors_found[color_id] = {
                'pos' : (int(color_x.mean()),int(color_y.mean())), #* get the mid pos
                'color': data['color'],
                'taken' : False,
            }
        
        


            print(f"found it: {self.colors_found[color_id]['pos']}\ncolor: {data['color']}")

        with open(self.color_file,'w') as f:
            json.dump(self.colors_found,f,indent=4)

    def make_check_point_image(self):
        camera_offset = camera_x,camera_y


        for points in self.colors_found.values():
            #* get the pos, multiply by zoom and reduce with camera x,y
            world_pos = (points['pos'][0]*player_car.zoom-camera_offset[0],points['pos'][1]*player_car.zoom-camera_offset[1])
            rect = self.time_adder_image.get_rect(center=world_pos)
            if not points['taken']:
                screen.blit(self.time_adder_image,rect)

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


            self.pixel_color =  self.road.get_at((int(x),int(y)))
    
            r,g,b = self.is_on()
            color = (r,g,b)
            color_bgr = [b,g,r]

            for data in self.colors_to_check.values():
                if data['color'] == color:
                    print('time _Added')
                    data['check'] = True
                    if not data['added_time']:
                        timer.add_time(10)
                        data['added_time'] = True

            for data in self.colors_found.values():
                if data['color'] == color_bgr:

                    print('color_taken, playing _sound')
                    if not data['taken']:
                        print('sound_played')
                        map_sound_manager.play('time_added','mp3')
                    data['taken'] = True
                    print(f'taken? = {data['taken']}')
                    map_sound_manager.reset_flag()

                    
                

                


        #for data in self.colors_to_check.values():
            #debug.debug_on_screen(f'check:{data['check']}', 'blue')

        #debug.debug_on_screen(f'on_this_color: {color}', 'yellow')
    def restart(self):
        for values in self.colors_to_check.values():
            values['check'] = False
            values['added_time'] = False

    def conclusion(self):
        self.check_colors()
        
        if pg.key.get_pressed()[pg.K_k]:
            self.race_end_test = True
        if all(v['check'] for v in self.colors_to_check.values()) or self.colors_to_check['color_1']['check'] or self.race_end_test:
            the_saved_data = savemanager.load_data()
            map_states_list = list(the_saved_data['map_states'])
            current_map_name = map_states_list[menu.selected_map_number]
            try:
                next_map_name = map_states_list[menu.selected_map_number+1]
            except IndexError:
                next_map_name = current_map_name
            the_saved_data['map_states'][next_map_name] = True
            next_unlock_state = the_saved_data
            savemanager.savedata(next_unlock_state)
            race_end()





def alot_of_images_for_racefinishanimation(file_name,file_path,files_num,extension = 'png',size=(100,100)):
    images = []
    for i in range(files_num):
        the_file = f'{file_path}/{file_name}_{i}.{extension}'
        image = pg.image.load(the_file)
        image = pg.transform.scale(image,(size))
        images.append(image)
    return images

class RaceFinishedAnimation:
    def __init__(self):
        global game_stat
        self.letter_images = alot_of_images_for_racefinishanimation('letter','race_end_assets',5,size=(300,300))
        self.total_width = sum(img.get_width() for img in self.letter_images)
        space = 20
        self.total_width += space*(len(self.letter_images)-1)
        start_x = (screen_width-self.total_width)//2
        rect = screen.get_rect()
        self.starting_pos = [
                (rect.left - self.letter_images[0].get_width(), rect.centery),      
                (rect.right + self.letter_images[0].get_width(), rect.centery),     
                (rect.centerx, rect.top - self.letter_images[0].get_width()),     
                (rect.centerx, rect.bottom + self.letter_images[0].get_width()),    
                (rect.left - self.letter_images[0].get_width(), rect.top - self.letter_images[0].get_width())     
            ]
        self.letters = []

        self.center_y = screen_height//2
        self.targets = []
        current_x = start_x

        for i,img in enumerate(self.letter_images):
            target_x = current_x
            target_y = self.center_y - img.get_height()//2

            starting_pos = self.starting_pos
            
            
            self.letters.append({
                "img": img,
                "x": starting_pos[i][0],
                "y": starting_pos[i][1],
                "target_x": target_x,
                "target_y": target_y,
                "done": False
            })
            current_x += img.get_width() + space
        self.finished_time = None
    def move_images(self):
        limit = 1

        for letter in self.letters:
            if not letter['done']:
                dx = letter['target_x'] - letter['x']
                dy = letter['target_y'] - letter['y']

                dis = math.hypot(dx,dy)

                if dis < limit:
                    letter['x'] = letter['target_x']
                    letter['y'] = letter['target_y']
                    letter['done'] = True
                else:
                    lerp_factor = 0.03
                    letter['x'] += (letter['target_x'] - letter['x']) * lerp_factor
                    letter['y'] += (letter['target_y'] - letter['y']) * lerp_factor

    def show_images(self):
        self.move_images()
        for letter in self.letters:
            screen.blit(letter["img"], (letter["x"], letter["y"]))


racefinishedanimations = RaceFinishedAnimation()

def race_end():
    global game_stat
    #bank.add_money(money_to_add)
    race_end_sound_manager.play('race_done','mp3')
    menu.update_lock_map()  
    if not player_car.dead:
        menu.reset_spawned_money(timer.time_left)
    game_stat = 'race_end_animation'


def end_animation():
    global game_stat

    audio = mutafile('race_end_assets/sounds/race_done.mp3')
    audio_length = audio.info.length*1000
    delay_after_audio = 0000
    
    delay_menu_time = audio_length + delay_after_audio  #* milliseconds only

    if game_stat == 'race_end_animation':
        timer.pause_time()
        racefinishedanimations.show_images()
        if all(letter["done"] for letter in racefinishedanimations.letters):
            if racefinishedanimations.finished_time is None:
                racefinishedanimations.finished_time = pg.time.get_ticks()            
            elif pg.time.get_ticks() - racefinishedanimations.finished_time > delay_menu_time:
                game_stat = 'menu'


def alot_of_images_for_GameOver(file_name,file_path='game_over_assets',files_num='2',extension = 'png',size=(100,100)):
    images = []
    for i in range(files_num):
        the_file = f'{file_path}/{file_name}_{i+1}.{extension}'
        image = pg.image.load(the_file)
        image = pg.transform.scale(image,(size))
        images.append(image)
    return images

class GameOver:
    def __init__(self):
        
        self.game_over_screen_alpha_rate = 0
        self.game_over_screen_fade = pg.Surface((screen_width, screen_height))
        self.game_over_screen_fade.fill((0,0,0))
        self.word_size = 300,300
        self.you_died_word = alot_of_images_for_GameOver('word',files_num=2,size=(self.word_size))
        #print(self.you_died_word)
        self.you_died = []

        self.total_width = self.word_size[0]*len(self.you_died_word)
        for i,word in enumerate(self.you_died_word):
            starting_x  = (screen_width-self.total_width)//2
            space = 30
            start_pos = [
                (screen_width+word.get_width(),screen.get_rect().centery),

                (0-word.get_width(),screen.get_rect().centery),
            ]
            target_pos = [
                (starting_x),  #* x values
                (starting_x+word.get_width()+space),
            ]

            img = word
            self.you_died.append({
                'img': img,
                'start_x': start_pos[i][0],
                'start_y': start_pos[i][1],
                'target_x': target_pos[i],
                'target_y': screen.get_rect().centery - img.get_height()//2,
                'x' : start_pos[i][0],
                'y' : start_pos[i][1],
                'done': False
            })
 
    def black_screen_effect(self):
        max_value = 255

        self.game_over_screen_alpha_rate += (max_value/300)
        
        if self.game_over_screen_alpha_rate < max_value:
            self.game_over_screen_fade.set_alpha(self.game_over_screen_alpha_rate)
        else:
            self.game_over_screen_fade.set_alpha(max_value)

        screen.blit(self.game_over_screen_fade,(0,0))

    def you_died_maker(self):
        limit = 1
        for word in self.you_died:
            if not word['done']:
                dx = word['target_x'] - word['x']
                dy = word['target_y'] - word['y']

                dis = math.hypot(dx,dy)
                if dis < limit:
                    word['x'] = word['target_x']
                    word['y'] = word['target_y']
                    word['done'] = True
                else:
                    lerp_factor = 0.03
                    word['x'] += (word['target_x'] - word['x']) * lerp_factor
                    word['y'] += (word['target_y'] - word['y']) * lerp_factor
                    
                    
                #print(f'dis: {dis},word_coords = {word['x'],word['y']}')
            screen.blit(word['img'],(word['x'],word['y']))
    def make(self):
        self.black_screen_effect()
        self.you_died_maker()

    
game_over_effects = GameOver()

def show_timer():
    pos = screen.get_rect()
    timer.show_time(screen,pos.topright)

check_points = Check_points()



def draw_on_game_on():

    
    tire_marks.make()
    player_car.draw()
    minimap.show_mini_map()
    show_timer()
    check_points.make_check_point_image()

def update_all():
    
    draw_map(camera_x,camera_y)
    tire_marks.show_tire_mark()
    tire_marks.update_tire_marks()
    pass

def world_logics():
    global game_stat

    check_points.conclusion()
    if game_stat == 'race_end_animation':
        end_animation()
    if game_stat == 'game_over' or game_over_effects.game_over_screen_alpha_rate > 0:
        game_over_effects.make()

loading_bar(100)
running = True
timer = Timer(race_time)

while running:
   

    global game_on
    dt = clock.tick(100)/1000
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False


    
    
    

    if game_stat != 'menu':
        update_all()
        draw_on_game_on()
        world_logics()

    
    elif game_stat == "menu":

        #pg.mixer.stop()
        car_sounds.stop_all()
        player_car.map.stop_threads()
        main_soundmanager.reset_flag()
        race_end_sound_manager.stop_all()
        race_end_sound_manager.reset_flag()

        player_car.map.loaded_chunks.clear()
        player_car.map.loaded_chunks = None
        player_car.raw_road_image = None
        player_car.road = None
        player_car.map = None
        player_car = None
        car_sounds = None
        tire_marks = None
        check_points = None
        the_map = None

        timer = None
        minimap = None
        menu.game_on = False
        racefinishedanimations = None
        game_over_effects = None

        gc.collect()

        pg.time.delay(100)  
        pg.event.clear()  
        #print(f'cleanup done, objects: {len(gc.get_objects())}')
        selected_car, selected_map = goto_menu()
        
        if selected_car is None or selected_map is None:
            running = False
            pg.quit()
            exit()
            
        loading_screen()

        
        loading_bar(30)
        
        fix_time_bug()
        player_car = Car(**garage[selected_car])
        timer = Timer(race_time)

        loading_bar(60)

        car_sounds = Car_sounds()
        racefinishedanimations = RaceFinishedAnimation()
        game_over_effects = GameOver()

        loading_bar(70)

        tire_marks = Tire_marks()
        minimap = MiniMap(player_car)
        check_points = Check_points()

        loading_bar(100)

        the_map = player_car.map
        timer.reset(race_time)
        #menu = None

        game_stat = "race"
        

    debug.show_bug(screen,screen_size)
    
    pg.display.flip()



pg.quit()
sys.exit()

#* 7 maps added, 3 left
#* add ending

    #//libpng warning: iCCP: known incorrect sRGB profile FIX THIS
    #// a lot of money spawing at the start after race ends, menu loading time?

#*//ram problem fixed, but the car is jittering
#* and the fps is getting tanked in menu because of the trails effect, removing it fully recovers the fps, but having it on and turning it to 0 changes nothing