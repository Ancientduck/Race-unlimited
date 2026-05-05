import pygame as pg
import math
import random
from kill_bug import debug
from factory import garage,maps

from shopsystem import shop
from SaveFileManager import savemanager
from trail_effect import MakeTrail
from car_stats import stats
from animation_manager import make_animation


the_font = 'Dragrace.ttf'
text_height = 30
font = pg.font.Font(the_font,text_height)

def CLICKING(events,rect):
    for e in events:
           if e.type == pg.MOUSEBUTTONDOWN:
               if rect.collidepoint(e.pos):
                    return True

def HOVERING(rect):
        if rect.collidepoint(pg.mouse.get_pos()):
             return True
        
def load_cars():
    car_list = []
    for values in garage.values():
        car_images = pg.image.load(values['image']).convert_alpha()
        car_images = pg.transform.smoothscale(car_images, (values['width'],values['height']))
        car_list.append(car_images)
    return car_list


def load_maps():
    map_images_list = []
    size = 200,200
    for values in maps.values():
         map_images = pg.image.load(values['thumbnail']).convert()
         map_images = pg.transform.smoothscale(map_images,(size))
         map_images_list.append(map_images)

    map_names_list = list(maps.keys())
    return map_images_list,map_names_list

def change_image_size(image,how_much: int):
     w,h = image.get_size()
     new_size = (int(w*how_much), int(h*how_much))
     return pg.transform.scale(image,new_size)
     

def filter_image(image,brightness=40):
     the_image = image.copy()
     the_image.fill((brightness,brightness,brightness), special_flags = pg.BLEND_RGB_ADD)
     return the_image

def get_image(name,extension = 'png'):
    path = f'menu_assets/{name}.{extension}'
    image = pg.image.load(path)
    return image

def alot_of_images(file_name,file_path,files_num,extension = 'png',size=(100,100)):
    images = []
    for i in range(files_num):
        the_file = f'{file_path}/{file_name} ({i+1}).{extension}'
        image = pg.image.load(the_file)
        image = pg.transform.scale(image,(size))
        images.append(image)
    return images

class ImageRotation():
    def __init__(self):
        self.angle = 0
    def continous_rotation(self,image,RPF,go_right= True):
        if go_right: 
           self.angle += RPF
        else: 
            self.angle -= RPF

        self.angle %= 360
        the_image = pg.transform.rotate(image,self.angle)
        return  the_image

#map_image_and_name_list = load_maps()

    
class SoundManager():
    def __init__(self):
        self.hover_sounds = {}
        self.sounds = {}
        
    def play(self,sound_name,extension='ogg'):
        if sound_name not in self.sounds:
            self.sounds[sound_name] = {
                'sound': pg.mixer.Sound(f'menu_assets/sounds/{sound_name}.{extension}'),
                'played': False
            }
        if self.sounds[sound_name]['played']:
            return
        self.sounds[sound_name]['sound'].play()
        self.sounds[sound_name]['played'] = True

    def hover_play(self,sound_name,extension='ogg',is_hover = True):
        if sound_name not in self.hover_sounds:
            self.hover_sounds[sound_name] = {
                    'sound' : pg.mixer.Sound(f'menu_assets/sounds/{sound_name}.{extension}'),
                    'played' : False,
                }

        if is_hover and not self.hover_sounds[sound_name]['played']:
            self.hover_sounds[sound_name]['sound'].play()
            self.hover_sounds[sound_name]['played'] = True
        

    def reset_flag(self):
        self.sounds.clear()

    def reset_hover_flag(self):
        self.hover_sounds.clear()

sound_manager = SoundManager()
down_wheel_manager = SoundManager()

loading_tips_list = [
    "Make sure to stay hydrated",
    "Is your device on?",
    "If you are stuck, buy a better car",
    "Do previous races again for better rewards",
    "More money = better car",
    "Just 1 minute",
    "sooo..how are you? :]",
    "let's GOOOOOOO",
    "Nice car",
    "Turing ON Music",
    "expect bugs :P",
    
]

font_for_loading = pg.font.Font(the_font,text_height)
class Menu:
    def __init__(self,screen,screen_size,selected_car_number=0,selected_map_number=0):
        #self.maketrail = MakeTrail(screen,12)
        self.angle = 0
        self.t = 0
        self.screen_size = screen_size
        self.play_btn_size = (200,200)
        self.quit_btn_size = self.play_btn_size

        self.play_button = pg.image.load('menu_assets/Play_btn.png').convert_alpha()
        self.play_button = pg.transform.scale(self.play_button,self.play_btn_size)


        self.quit_btn = pg.image.load('menu_assets/quit_btn.png').convert_alpha()
        self.quit_btn = pg.transform.scale(self.quit_btn,(self.quit_btn_size))

        self.game_on = False
        self.quit_game = False
        self.selected_car_number = 0

        self.bg = pg.image.load('menu_assets/bg.png').convert_alpha()
        self.bg = pg.transform.smoothscale(self.bg,(screen_size))

        

        self.help_btn = pg.image.load('menu_assets/question_mark.png').convert_alpha()
        self.help_btn_size = 100,100
        self.help_btn = pg.transform.scale(self.help_btn,self.help_btn_size)
        self.selected_car_numbern_menu = None
        
        self.car_images_list = load_cars()
        self.map_images_list,self.map_names_list = load_maps()

        self.base_wheel_png_left = pg.image.load("menu_assets/wheel.png")
        self.base_wheel_png_right = pg.image.load("menu_assets/wheel.png")
        self.wheel_png_size = (100,100)

        self.base_wheel_png_left = pg.transform.smoothscale(self.base_wheel_png_left,self.wheel_png_size)
        self.base_wheel_png_right = pg.transform.smoothscale(self.base_wheel_png_right,self.wheel_png_size)

        self.wheel_png_left = pg.image.load("menu_assets/wheel.png")
        self.wheel_png_right = pg.image.load("menu_assets/wheel.png")

        self.wheel_png_left = pg.transform.smoothscale(self.wheel_png_left,self.wheel_png_size)
        self.wheel_png_right = pg.transform.smoothscale(self.wheel_png_right,self.wheel_png_size)

        self.big_wheel_png_left = change_image_size(self.wheel_png_left,1.5)
        self.big_wheel_png_right = change_image_size(self.wheel_png_right,1.5)
    

        self.selected_car_number = selected_car_number
        self.selected_map_number = selected_map_number 
      
        self.wheel_left_rect = None
        self.wheel_right_rect = None

        self.car_rotation = ImageRotation()

        self.wheel_rotation_left = ImageRotation()
        self.wheel_rotation_right = ImageRotation()

        self.big_wheel_rotationg_left = ImageRotation()
        self.big_wheel_rotationg_right = ImageRotation()

        
        self.spawned_money = True
        self.should_show_money = False
        self.bonus = 0

        self.map_holder_size  = (300,280)
        self.map_holder_img = get_image('map_holder').convert_alpha()   
        self.map_holder_img = pg.transform.scale(self.map_holder_img,self.map_holder_size)


        self.chain = get_image('chain').convert_alpha()
        self.chain = pg.transform.smoothscale(self.chain,(200,100))
        self.car_unlock_state_data_load = savemanager.load_data()
        self.map_unlock_state_data_load = savemanager.load_data()

        self.dark_place_holder = get_image('dark_place_holder').convert_alpha()
        self.dark_place_holder = pg.transform.scale(self.dark_place_holder,(400,200))

        self.red_place_holder = get_image('price_holder').convert_alpha()
        self.red_place_holder = pg.transform.scale(self.red_place_holder,(400,200))
        
        self.lock_frame_images_size = self.map_holder_img.get_rect().inflate(-100,-80).size
        self.name_lock_frame_images_size = self.red_place_holder.get_rect().inflate(-30,-30).size

        self.lock_frame_images = alot_of_images('lock_frame','menu_assets/lock_frames',15,'png',self.lock_frame_images_size)
        self.map_name_lock_frame_images = alot_of_images('lock_frame','menu_assets/lock_frames',15,'png',self.name_lock_frame_images_size)
    
        self.map_tn_size = self.map_images_list[0].get_size()
        self.round_corners_for_map_img = pg.Surface((self.map_tn_size), pg.SRCALPHA)
        self.radius = 20  # adjust for how round you want
        
        self.choosen_tip = random.choice(loading_tips_list)
        self.tip_background = None

        self.background_gradient_color = draw_red_gradient(self.screen_size,t=self.t)
    def play(self,screen,events):
        height_fix = 100
        screen_x = 200
        screen_y = screen.get_height() // 2 - height_fix
        pos = (screen_x-self.play_btn_size[0]//2,screen_y-self.play_btn_size[1]//2)

        rect = self.play_button.get_rect(topleft=pos)
        
        if CLICKING(events,rect):
            save_data = savemanager.load_data()
            car_name = list(garage.keys())[self.selected_car_number]
            map_name = list(maps.keys())[self.selected_map_number]
            if save_data['car_state'][car_name] and save_data['map_states'][map_name]:
                self.game_on = True
                print(save_data['car_state'][car_name])
            
            else:
                print('you are poor or lazy')

        if HOVERING(rect):
            screen.blit(filter_image(self.play_button),pos)

        else:
            screen.blit(self.play_button,pos)
    
    def change_tips(self):
        new_tip = random.choice(loading_tips_list)
        while new_tip == self.choosen_tip:
            new_tip = random.choices(loading_tips_list)
        self.choosen_tip = new_tip

    def loading_tips(self,screen,bar_rect):
        text_color = (180, 220, 255)
        shadow_color = (0, 0, 40)



        loading_tip_text = font_for_loading.render(f'Tip: {self.choosen_tip}',True,text_color)
        
        loading_tip_text_rect = loading_tip_text.get_rect(midbottom = bar_rect.midtop)

        shadow_text = font_for_loading.render(f'Tip: {self.choosen_tip}',True,shadow_color)
        shadow_text_rect = shadow_text.get_rect(center=(loading_tip_text_rect.centerx+5,loading_tip_text_rect.centery+5))
        


        screen.blit(shadow_text,shadow_text_rect)
        screen.blit(loading_tip_text,loading_tip_text_rect)


    def quit_button(self,screen,events):
        height_fix = 200
        screen_x = 200
        screen_y = screen.get_height() // 2 + height_fix
        pos = (screen_x-self.play_btn_size[0]//2,screen_y-self.play_btn_size[1]//2)

        rect = self.quit_btn.get_rect(topleft=pos)
       

        if CLICKING(events,rect):
            self.quit_game = True
            print('clicked '+'now_game_is: '+str(self.quit_game))

        if HOVERING(rect):
            screen.blit(filter_image(self.quit_btn),pos)

        else:
            screen.blit(self.quit_btn,pos)

    def helper(self,screen,events):
        height_fix = 50
        screen_x = 200
        screen_y = screen.get_height() // 2 + height_fix
        pos = (screen_x-self.play_btn_size[0]//2,screen_y-self.play_btn_size[1]//2)

        rect = self.help_btn.get_rect(topleft=pos)

        if CLICKING(events,rect):
            self.menu = 'menu'

        if HOVERING(rect):
             screen.blit(filter_image(self.help_btn),pos)
        else:
            screen.blit(self.help_btn,pos)

    def show_cars(self,screen,events):
            



            height_fix = 0
            screen_x = screen.get_width() // 2 
            screen_y = screen.get_height() // 2 - height_fix
            car_pos = (screen_x,screen_y)

            #car_img = self.select_car()[0]
            original_car_image = self.car_images_list[self.selected_car_number]

            original_wheel_png_left = self.wheel_png_left
            original_wheel_png_right = self.wheel_png_right

            original_big_wheel_png_left = self.big_wheel_png_left
            original_big_wheel_png_right = self.big_wheel_png_right

            wheel_png_left = original_wheel_png_left
            wheel_png_right = original_wheel_png_right

            big_wheel_png_left = original_big_wheel_png_left
            big_wheel_png_right = original_big_wheel_png_right


            rpf_for_wheels = 2
            car_name = list(garage.keys())[self.selected_car_number]
            if  shop.return_car_state(car_name):
                wheel_png_left = self.wheel_rotation_left.continous_rotation(original_wheel_png_left,rpf_for_wheels,False)
                wheel_png_right = self.wheel_rotation_right.continous_rotation(original_wheel_png_right,rpf_for_wheels,True)

                big_wheel_png_left = self.big_wheel_rotationg_left.continous_rotation(original_big_wheel_png_left,rpf_for_wheels,False)
                big_wheel_png_right = self.big_wheel_rotationg_right.continous_rotation(original_big_wheel_png_right,rpf_for_wheels,True)
            

            car_img = self.car_images_list[self.selected_car_number]
            car_rect = car_img.get_rect(center=car_pos)
            
            pos = (car_rect.center[0] - 300 , car_rect.centery)
            pos2 = (car_rect.center[0] + 300 , car_rect.centery)



            wheel_left_rect = wheel_png_left.get_rect(center = pos)
            wheel_right_rect = wheel_png_right.get_rect(center = pos2)


            car_list = list(garage.keys())
            
            switch_car_state  = self.car_unlock_state_data_load['car_state'][car_name]
            if self.selected_car_number < len(car_list)-1:   
                if CLICKING(events,wheel_right_rect):
                    self.selected_car_number += 1
                    sound_manager.play('pressed_gear_sound')
                    self.car_unlock_state_data_load = savemanager.load_data()
       

                else:
                    sound_manager.reset_flag()

            if self.selected_car_number > 0:
                if CLICKING(events,wheel_left_rect):
                    self.selected_car_number -= 1
                    sound_manager.play('pressed_gear_sound')
                    self.car_unlock_state_data_load = savemanager.load_data()
       


                else:
                    sound_manager.reset_flag()
            
            original_car_image = self.car_images_list[self.selected_car_number]
            car_img = self.car_rotation.continous_rotation(original_car_image,1)
            car_rect = car_img.get_rect(center=car_pos)



            big_wheel_left_rect = big_wheel_png_left.get_rect(center = pos)
            big_wheel_right_rect = big_wheel_png_right.get_rect(center = pos2)

            if HOVERING(wheel_left_rect):
                 
                screen.blit(big_wheel_png_left,big_wheel_left_rect)

            else:
                screen.blit(wheel_png_left,wheel_left_rect)


            if HOVERING(wheel_right_rect):
                screen.blit(big_wheel_png_right,big_wheel_right_rect)

            else:
                screen.blit(wheel_png_right,wheel_right_rect)


            if HOVERING(wheel_left_rect) or HOVERING(wheel_right_rect):
                down_wheel_manager.hover_play('hover_sound','mp3')
            else:
                down_wheel_manager.reset_hover_flag()
            
            

            switch_car_state  = self.car_unlock_state_data_load['car_state'][car_name]



            # if not car_state:
            #     self.car_unlock_state_data_load = savemanager.load_data()
            #     self.car_unlock_state_data_load['car_state'][car_name]
                
            #     car_state  = self.car_unlock_state_data_load['car_state'][car_name]

            screen.blit(car_img,car_rect)
            chain_width = abs(pos[0] - pos2[0])
            chain_rect = self.chain.get_rect(midleft = pos )

            buy_car_state = shop.car_state_for_menu
            #debug.debug_on_screen(f'buy_car_state: {buy_car_state}\n switch_car_state: {switch_car_state}','yellow')

            if not shop.return_car_state(car_name):
                self.show_chain(chain_rect,chain_width,screen)
    
            self.show_car_stats(car_name,screen)
    def show_car_stats(self,car_name,screen):
        stats.show_data(car_name,screen)


    def show_chain(self,pos,chain_width,screen):

        self.chain = pg.transform.scale(self.chain,(chain_width,100))
        screen.blit(self.chain,pos)

        
    def select_car(self):
        selected_car =  list(garage.keys())[self.selected_car_number] 
        car_img = self.car_images_list[self.selected_car_number].convert_alpha()
        return car_img,selected_car 
    
    def select_map(self):
        selected_map = list(maps.keys())[self.selected_map_number]
        map_image = self.map_images_list[self.selected_map_number].convert()

        return map_image,selected_map

    def show_map(self,screen,events):
        height_fix = 200
        screen_x = screen.get_width() // 2 
        screen_y = screen.get_height() // 2 - height_fix

        map_image = self.select_map()[0]
        map_pos = (screen_x,screen_y)

        map_rect = map_image.get_rect(center=map_pos)


    
        original_wheel_png_left = self.wheel_png_left
        original_wheel_png_right = self.wheel_png_right

        original_big_wheel_png_left = self.big_wheel_png_left
        original_big_wheel_png_right = self.big_wheel_png_right

        wheel_png_left = original_wheel_png_left
        wheel_png_right = original_wheel_png_right

        big_wheel_left = original_big_wheel_png_left
        big_wheel_right = original_big_wheel_png_right


        rpf_for_wheels = 1
        #wheel_png_left = self.wheel_rotation_left.continous_rotation(original_wheel_png_left,rpf_for_wheels,False)
        #wheel_png_right = self.wheel_rotation_right.continous_rotation(original_wheel_png_right,rpf_for_wheels,True)

        #big_wheel_left = self.big_wheel_rotationg_left.continous_rotation(original_big_wheel_png_left,rpf_for_wheels,False)
        #big_wheel_right = self.big_wheel_rotationg_right.continous_rotation(original_big_wheel_png_right,rpf_for_wheels,True)
        
        pos = (map_rect.center[0] - 200 , map_rect.centery)
        pos2 = (map_rect.center[0] + 200 , map_rect.centery)

        wheel_left_rect = wheel_png_left.get_rect(center = pos)
        wheel_right_rect = wheel_png_right.get_rect(center = pos2)

        map_name_list = list(maps.keys())
        map_list = list(maps.keys())
        map_holder_rect = self.map_holder_img.get_rect(center=map_rect.center)

        

        screen.blit(self.map_holder_img,map_holder_rect)        

        if self.selected_map_number < len(map_list)-1:   
            if CLICKING(events,wheel_right_rect):
                self.selected_map_number += 1
                map_image = self.select_map()[0]
                sound_manager.play('flip_page','wav')
            else:
                sound_manager.reset_flag()
        if self.selected_map_number > 0:
            if CLICKING(events,wheel_left_rect):
                self.selected_map_number -= 1
                map_image = self.select_map()[0]
                sound_manager.play('flip_page','wav')
            else:
                sound_manager.reset_flag()

        big_wheel_left_rect = big_wheel_left.get_rect(center = pos)
        big_wheel_right_rect = big_wheel_right.get_rect(center = pos2)

        if HOVERING(wheel_left_rect):
            screen.blit(big_wheel_left,big_wheel_left_rect)

        else:
            screen.blit(wheel_png_left,wheel_left_rect)


        if HOVERING(wheel_right_rect):
            screen.blit(big_wheel_right,big_wheel_right_rect)
            
        else:
            screen.blit(wheel_png_right,wheel_right_rect)

        if HOVERING(wheel_left_rect) or HOVERING(wheel_right_rect):
            sound_manager.hover_play('hover_sound','mp3')
        else:
            sound_manager.reset_hover_flag()


        map_name_place_holder = self.red_place_holder

        map_name_holder_rect = map_name_place_holder.get_rect(midbottom=map_rect.midtop)
        
        map_name = map_name_list[self.selected_map_number]
 
        dark_neon_blue = (0, 200, 255)
        green = (0, 255, 0)
        black = (0,0,0)


        map_name_text = font.render(f'{map_name}',True,black)

        map_name_text_rect = map_name_text.get_rect(center=map_name_holder_rect.center)

        map_prize = maps[map_name]['prize']
        map_prize_text = font.render(f'prize: ${map_prize:,}',True,green)
        map_prize_text_rect = map_prize_text.get_rect(midtop=map_name_text_rect.midbottom)

        screen.blit(map_name_place_holder,map_name_holder_rect)
        screen.blit(map_name_text,map_name_text_rect)
        screen.blit(map_prize_text,map_prize_text_rect)
        
        pg.draw.rect(self.round_corners_for_map_img, (255,255,255,255), (0, 0, *self.map_tn_size), border_radius=self.radius) #* to round the corners of the map
        self.round_corners_for_map_img.blit(map_image,(0,0),special_flags=pg.BLEND_RGBA_MULT)

        screen.blit(self.round_corners_for_map_img,map_rect) 
        
        self.lock_map(screen,map_name,map_rect,map_name_text_rect)


    def update_lock_map(self):
        self.map_unlock_state_data_load = savemanager.load_data()
        
    def lock_map(self,screen,map_name,map_rect,map_name_text_rect):
        the_states = self.map_unlock_state_data_load['map_states']

        frame_images = self.lock_frame_images
        map_lock_frame = make_animation.get_frame(frame_images)
        frame_location = map_lock_frame.get_rect(center=map_rect.center)

        name_lock_images = self.map_name_lock_frame_images
        name_lock_frames = make_animation.get_frame(name_lock_images)
        name_lock_frame_location = name_lock_frames.get_rect(center=map_name_text_rect.center)
        
        if the_states[map_name] == False:
            screen.blit(map_lock_frame,frame_location)
            screen.blit(name_lock_frames,name_lock_frame_location)
            
    def show_buy_btn(self,screen,events):
        height_fix = 0
        screen_x = screen.get_width() // 2 - 200
        screen_y = screen.get_height() // 2 - height_fix

        buy_pos = (screen_x,screen_y+250)
        price_pos = (screen_x+200,screen_y+200)
        name = list(garage.keys())[self.selected_car_number]
        shop.car_buy_btn(name,screen,buy_pos,events)
        shop.show_price(name,screen,price_pos)
        

    def reset_spawned_money(self,bonus:int):
        self.spawned_money = False
        self.bonus = bonus

    def showing_money(self,screen):
        from banksystem import bank
        
        if not self.spawned_money:
            selected_map = list(maps.keys())[self.selected_map_number]
            prize = maps[selected_map]['prize']
            bank.prize = prize
            bank.spawn_money(screen,prize,self.bonus)
            self.spawned_money = True
        bank.show_money(screen)
        #bank.show_bank(screen)


    def background_menu(self,screen):
        #self.t += 0.02
        gradient = self.background_gradient_color
        #overlay = get_overlay(self.screen_size,self.t)

        screen.blit(gradient,(0,0))
        #screen.blit(overlay, (0, 0))
        #self.maketrail.draw_lines(screen)
        screen.blit(self.bg,(0,0))


        


# def draw_red_gradient(screen_size, intensity=100, t=0):
#     """Draws gradient based on intensity."""
#     width, height = screen_size
#     gradient = pg.Surface((width, height))
#     offset = math.sin(t * 0.5) * 50
#     center_y = height / 2 + offset    

#     # Darker neon blue tone (reduced green & blue)
#     base_rgb = (0, 120, 200)
    
#     for y in range(height):
#         dist = abs(y - center_y) / center_y
#         factor = max(0, (1 - dist)) * (intensity / 100)

#         color_value_2 = max(0, min(255, int(base_rgb[1] * factor)))
#         color_value   = max(0, min(255, int(base_rgb[2] * factor)))
#         gradient.fill((0, color_value_2, color_value), rect=pg.Rect(0, y, width, 1))

#     return gradient

def draw_red_gradient(screen_size,intensity= 100,t=0):
    """Draws  gradient based on intensity."""
    width,height = screen_size
    gradient = pg.Surface((width, height))
    offset = math.sin(t*0.5)*50
    center_y = height/2 + offset    

    rgb = (255, 0, 0)
    
    for y in range(height):
        dist = abs(y-center_y)/center_y
        color_value = max(0, min(255, int(intensity * (1 - dist))))
        color_value_2 = max(0, min(100, int(intensity * (1 - dist))))
        gradient.fill((color_value,0,0), rect=pg.Rect(0,y,width,1))

        #NOTE: color value on blue part gives the correct neon blue color
    return gradient

def get_overlay(screen_size,t):
    overlay = pg.Surface(screen_size,pg.SRCALPHA)  #
    alpha =  70 + int(50 * math.sin(t))  
    overlay.fill((255, 0, 0, abs(alpha)))
    return overlay



## FIX HOVERING SOUND EFFECT REPEATING
    #cause: if you hover on map wheels the reset flags on the show cars will work cause you are not hovering on that, THINK
    #solulu: made another instance for the down sound manager