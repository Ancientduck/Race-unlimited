import pygame as pg

from SaveFileManager import savemanager
from soundsystem import SoundManager
from factory import garage,maps
import random
import time
import math



sound_manager = SoundManager('menu_assets/sounds')

def get_money():
    data = savemanager.load_data()
    if 'balance' in data:
        return data['balance']
    else:
        return 0
font = pg.font.Font('Dragrace.ttf',28)

class Dollar(pg.sprite.Sprite):
    def __init__(self,screen,images,pos,timer,rate_of_scale=5,target=50):
        super().__init__()
        self.image_dict = images
        self.pos = pg.math.Vector2(pos)
        self.timer = timer
        
        self.rate_of_scale = rate_of_scale
        self.target = target
        self.scale_start = 1

        
        self.size = int(self.scale_start)
        self.image = self.image_dict[self.size]
        self.rect = self.image.get_rect(center=self.pos)

        self.start_time = pg.time.get_ticks()
        self.alive = True

        self.screen = screen
    def update(self,wallet_pos):
        if not bank.should_show_money:
            return
        now = pg.time.get_ticks() - self.start_time
        if now > self.timer:
            if self.scale_start <= self.target:
                self.scale_start += self.rate_of_scale
                if self.scale_start > self.target:
                    self.scale_start = self.target
        self.size = int(self.scale_start)
        self.image = self.image_dict[self.size]
        self.rect = self.image.get_rect(center=self.pos)

        self.move_to_wallet(self.screen,now,wallet_pos,40)

        
    def move_to_wallet(self,screen,now,target_pos,speed = 20):
        target = pg.math.Vector2(target_pos)
        direction = target - self.pos
        speed = speed
        if now > self.timer + 100:
            if direction.length() > speed:
                velocity = direction.normalize() * speed
                self.pos += velocity
                self.rect.center = self.pos
            else:
                
                self.pos = target
                self.rect.center = self.pos
                bank.dollar_reached = True
                bank.money_given += 1
                #self.alive = False
                self.reset(screen)

                bank.add_money()
                sound_manager.reset_flag()
            if direction.length() < 5:
                bank.dollar_reached = True
                
                sound_manager.play('money_reached','mp3')
    def reset(self,screen):
        zone = pg.Rect(0, 0, 1000, 300)
        zone.midbottom = screen.get_rect().midbottom
        max_x = zone.right - bank.one_dollar.get_width()
        max_y = zone.bottom - bank.one_dollar.get_height()
        x = random.randint(zone.x, max_x)
        y = random.randint(zone.y, max_y)
        
        
        pos = (x,y)
        self.pos = pg.math.Vector2(pos)
        self.rate_of_scale = 5
        self.target = self.target
        self.scale_start = 1
        self.start_time =  pg.time.get_ticks()
        self.timer = 1
        self.alive = True



class Bank:
    def __init__(self,screen):
        self.current_money = get_money()
        self.money_img = pg.image.load('menu_assets\stack_of_money.png')
        self.money_img = pg.transform.smoothscale(self.money_img,(100,70))

        self.money_larger_img = pg.transform.smoothscale(self.money_img,(130,90))
        self.one_dollar = pg.image.load('menu_assets/one_dollar.png').convert_alpha()
        self.one_dollar = pg.transform.smoothscale(self.one_dollar,(50,50)).convert_alpha()
 
        self.scaled_dollars = {}

        self.scale_start = 1
        self.rate_of_scale = 5
        self.target = 50

        self.should_show_money = False

        while self.scale_start <= self.target:
            size = int(self.scale_start)
            self.scale_start += self.rate_of_scale
            scaled_image = pg.transform.smoothscale(self.one_dollar,(size,size))
            self.scaled_dollars[size] = scaled_image

        if self.target not in self.scaled_dollars:
            self.scaled_dollars[self.target] = pg.transform.smoothscale(self.one_dollar, (self.target, self.target))

        self.dollar_reached = False

        self.prize_money = 0
        self.money_given = 0
        self.bonus = 0
        self.amount = 0
    
        self.dollars_for_use = pg.sprite.Group()


        self.all_money_given = False
        zone = pg.Rect(0, 0, 1000, 300)
        zone.midbottom = screen.get_rect().midbottom

        max_x = zone.right - self.one_dollar.get_width()
        max_y = zone.bottom - self.one_dollar.get_height()
        x = random.randint(zone.x, max_x)
        y = random.randint(zone.y, max_y)
        self.dollars_for_use_amount = 100
        for i in range(self.dollars_for_use_amount):

            x = random.randint(zone.x, max_x)
            y = random.randint(zone.y, max_y)
            pos = (x, y)
            timer = 1
            alive = True
            dollar = Dollar(screen,self.scaled_dollars, pos, timer,self.rate_of_scale,self.target)
            self.dollars_for_use.add(dollar)

    def add_money(self,all_at_once=False):
        if not all_at_once:
            self.current_money += 1
            savemanager.savedata({'balance': self.current_money})
        elif all_at_once:
            self.current_money += self.prize_money - self.money_given
            savemanager.savedata({'balance': self.current_money})


    def reduce_money(self,amount):
        self.current_money -= amount
        savemanager.savedata({'balance': self.current_money})

    def spawn_money(self,screen,amount,bonus = 0):

        bonus_money = bonus * 100
        self.amount = amount
        self.bonus = bonus_money
        self.prize_money = int(self.bonus + self.amount)
        self.money_given = 0
        self.all_money_given = False
        self.should_show_money = False

        for dollar in self.dollars_for_use:
            dollar.reset(screen)

        
    
        
    def show_money(self, screen):
        
        zone = pg.Rect(0, 0, 1000, 300)
        zone.midbottom = screen.get_rect().midbottom
        #pg.draw.rect(screen, (255, 0, 0), zone, 2)
        self.prize_money = int(self.bonus + self.amount)
        pos = (screen.get_width() - self.money_img.get_width() - 30, 20)
        money_pos_rect = self.money_img.get_rect(topleft=pos)
        money_larger_pos_rect = self.money_larger_img.get_rect(center = money_pos_rect.center)

        text = font.render(f'${self.current_money:,}', True, (0, 255, 0))

        text_rect = text.get_rect(topright=money_pos_rect.midleft)
        
        
        #self.absolute_dollar_group = [self.dollar_group,self.dollar_group_2,self.dollar_group_3,self.dollar_group_4,self.dollar_group_5,self.dollar_group_6,self.dollar_group_7,self.dollar_group_8,self.dollar_group_9,self.dollar_group_10]

        absolute_money_value = self.prize_money - self.money_given

        money_going_text = font.render(f'+ ${absolute_money_value:,}', True, (0, 255, 0))

        money_going_rect = money_going_text.get_rect(topright=text_rect.bottomright)
        money_going_rect.y += 5

        if not self.dollar_reached or absolute_money_value <= 0:
            screen.blit(self.money_img, money_pos_rect)
            text_rect = text.get_rect(topright=money_pos_rect.midleft)
            
        elif self.dollar_reached:
            screen.blit(self.money_larger_img,money_larger_pos_rect)
            text_rect = text.get_rect(topright=money_larger_pos_rect.midleft)

        text_rect.x -= 0
        text_rect.y -= 10
        screen.blit(text, text_rect)
        if absolute_money_value > 0:
            screen.blit(money_going_text,money_going_rect)

        if absolute_money_value > 0:
            self.should_show_money = True

        money_left_to_give = self.prize_money - self.money_given
        if money_left_to_give > 0:
            self.dollars_for_use.update(money_pos_rect.center)
            self.dollars_for_use.draw(screen)


        if pg.mouse.get_pressed()[0] and absolute_money_value > 0:
            self.add_money(all_at_once=True)
            self.all_money_given = True
            self.money_given = self.prize_money
            self.should_show_money = False
        
#///* to do: make it scaleable 
#bank = Bank()
bank = None
def make_bank(screen):
    global bank
    bank = Bank(screen)
    return bank



