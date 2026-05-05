import pygame as pg
from factory import garage,maps
from SaveFileManager import savemanager
from kill_bug import debug

pg.init()
pg.display.set_caption('racing')

car_list = list(garage.keys())
map_list = list(maps.keys())
class DataLoader:
    def __init__(self):
        self.save_data = savemanager.load_data()
    def get_car(self):
        if 'the_car' in self.save_data:
            return  self.save_data['the_car']
        else:
            return car_list[0]
    def get_map(self):
        if 'the_map' in self.save_data:
            return self.save_data['the_map']
        else:
            return map_list[0]
        
dataloader = DataLoader()



def run_menu(screen,menu):
    global car_list,map_list

    selected_car_number = car_list.index(dataloader.get_car())
    selected_map_number = map_list.index(dataloader.get_map())

    #menu = Menu(screen.get_size(),selected_car_number,selected_map_number)
    clock = pg.time.Clock()
    
    selected_car = None
    selected_map = None
    running = True
    while running:
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT:
                pg.quit()
                exit()
        
        debug.debug_on_screen(f'{clock.get_fps()}','blue')
        menu.background_menu(screen)
   
        menu.show_cars(screen, events)
        #menu.helper(screen, events)
        menu.play(screen, events)
        menu.quit_button(screen,events)
        menu.show_map(screen,events)
        menu.showing_money(screen)
        menu.show_buy_btn(screen,events)
        if menu.game_on:

            
            selected_car = menu.select_car()[1]  # get the key name of the selected car
            selected_map = menu.select_map()[1]   #get the key name of the selected map


            data_to_save = {'the_car': selected_car,
                            'the_map': selected_map
                            }
            savemanager.savedata(data_to_save)
            running = False
        if menu.quit_game:
            selected_car = menu.select_car()[1]  # get the key name of the selected car
            selected_map = menu.select_map()[1]   #get the key name of the selected map


            data_to_save = {'the_car': selected_car,
                            'the_map': selected_map
                            }
            savemanager.savedata(data_to_save)
            running = False
            return None,None
            
        debug.show_bug(screen,screen.get_size())
        pg.display.update()
        clock.tick(100)

    return selected_car,selected_map