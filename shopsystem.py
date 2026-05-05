import pygame as pg
from factory import garage
from SaveFileManager import savemanager

from soundsystem import SoundManager
from kill_bug import debug

soundmanager = SoundManager('menu_assets/sounds')
font = pg.font.Font('Dragrace.ttf',28)
class DataLoader:
    def __init__(self):
        self.save_data = savemanager.load_data()

    def get_car_state(self):
        self.save_data = savemanager.load_data()
        if 'car_state' in self.save_data:
            return  self.save_data['car_state']
        else:
            return None
    def get_money(self):
        self.save_data = savemanager.load_data()
        if 'balance' in self.save_data:
                return self.save_data['balance']
        else:
                return 0
        
dataloader = DataLoader()

def HOVERING(rect):
        if rect.collidepoint(pg.mouse.get_pos()):
             return True
def CLICKING(events,rect):
    for e in events:
           if e.type == pg.MOUSEBUTTONDOWN:
               if rect.collidepoint(e.pos):
                    return True
               
class Shop:
    def __init__(self):

        self.car_states = dataloader.get_car_state()
        self.base_buy_btn = pg.image.load('menu_assets/buy_btn.png')
        self.buy_btn = pg.transform.smoothscale(self.base_buy_btn,(200,200))
        self.bigger_buy_btn = pg.transform.smoothscale(self.base_buy_btn,(300,300))
        self.current_balance = dataloader.get_money()

        self.price_holder = pg.image.load('menu_assets/price_holder.png')
        self.price_holder = pg.transform.smoothscale(self.price_holder,(300,100))
        self.buy_btn_current_rect = None
        self.car_state_for_menu = False
    def car_buy_btn(self,car_name,screen,pos,events):
        if self.car_states[car_name]:
            return
        self.rect = self.buy_btn.get_rect(center = pos)
        self.bigger_rect = self.bigger_buy_btn.get_rect(center = pos)
        if not HOVERING(self.rect):
            screen.blit(self.buy_btn,self.rect)
            self.buy_btn_current_rect = self.rect
        else:
            screen.blit(self.bigger_buy_btn,self.bigger_rect)
            self.buy_btn_current_rect = self.bigger_rect
        price = garage[car_name]['price']
        
        
        if CLICKING(events,self.rect):
            self.current_balance = dataloader.get_money()
            money_left = (self.current_balance - price)
     
            if money_left >= 0:
                from banksystem import bank
                self.current_balance = money_left
                self.car_states[car_name] = True
                save_data = savemanager.load_data()
                save_data['car_state'][car_name] = True
                data_to_save = save_data 
                savemanager.savedata(data_to_save)
                bank.reduce_money(price)
                soundmanager.play('buy','mp3')
                soundmanager.reset_flag()
    
                

    def return_car_state(self,car_name):
        return self.car_states[car_name]
    def show_price(self,car_name,screen,pos):
        if self.car_states[car_name]:
            return 
        price = garage[car_name]['price']
        text = font.render(f'${price:,}', True, (0, 255, 0))

        text_rect = text.get_rect()
        price_holder_pos = self.price_holder.get_rect(midleft = self.buy_btn_current_rect.midright)
        text_rect.center = price_holder_pos.center
        screen.blit(self.price_holder,price_holder_pos)
        screen.blit(text,text_rect)


shop = Shop()