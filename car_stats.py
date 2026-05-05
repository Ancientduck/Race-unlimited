import pygame as pg
from factory import garage
the_font = 'Dragrace.ttf'
text_height = 20
font = pg.font.Font(the_font,text_height)



def loading_bar(x,y,w_now,screen,data_name,color = 'neon',):
    w,h = w_now,20
    out_ln_w,out_ln_h = 10,10

    


    if color == 'blue':
        rgb = (0,0,255)
    elif color == 'green':
        rgb = (0,255,0)
    elif color == 'red':
        rgb = (255,0,0)
    elif color == 'neon':
        rgb = (0, 200, 255)

    
    if data_name == 'handling':
        w_now = 200*w_now
    elif data_name == 'max_speed':
        w_now = w_now/15
    elif data_name == 'acceleration':
        w_now = w_now/5
    else:
        w_now = 10*w_now

    outline =  pg.draw.rect(screen,(0,0,0),(x,y,w_now+out_ln_w,h+out_ln_h))  #*outline

    bar_rect = pg.Rect(0,0,w_now,h)
    bar_rect.midleft = (outline.midleft[0] + 5 , outline.midleft[1])
    drawing_bar = pg.draw.rect(screen,rgb,bar_rect)
    
    

def get_image(name,extension = 'png'):
    path = f'menu_assets/{name}.{extension}'
    image = pg.image.load(path)
    return image

def scale_image(image,size):
    return pg.transform.scale(image,size)
class Stats:
    def __init__(self,):
        self.place_holder = get_image('dark_place_holder')
        self.place_holder = scale_image(self.place_holder,(300,100))

    def get_numbers(self,car_name):
        self.selected_car = car_name
        car_data = {
            'acceleration': garage[self.selected_car]['acceleration'],
            'max_speed': garage[self.selected_car]['max_speed'],  
            'brake':  garage[self.selected_car]['brake'],
            'handling':  garage[self.selected_car]['handling'],
        }

        return car_data
    def show_data(self,car_name,screen):
        
        car_data = self.get_numbers(car_name)
        dark_neon_blue = (0, 200, 255)
        for i,(name,data) in enumerate(car_data.items()):
            screen_rect =  screen.get_rect()
            text_data = f"{name}:"
            text = font.render(text_data,True,dark_neon_blue)
            x = screen_rect.midbottom[0]
            y = (screen_rect.midbottom[1] - 100) -  (i * (text_height + 5))
            text_rect = text.get_rect(center = (x,y))

 
            bar_pos = (screen_rect.midbottom[0] + 70 ,text_rect.midright[1])
            loading_bar(bar_pos[0]+text_height,bar_pos[1]-text_height,data,screen,name)
            screen.blit(text,text_rect)

        self.place_holder.convert_alpha()
        place_holder_rect = self.place_holder.get_rect(center = screen_rect.center)
        place_holder_rect.y += 130
        car_name_text = font.render(car_name,True,dark_neon_blue)

        car_name_text_rect = car_name_text.get_rect(center = place_holder_rect.center)


        screen.blit(self.place_holder,place_holder_rect)
        screen.blit(car_name_text,car_name_text_rect)

stats = Stats()