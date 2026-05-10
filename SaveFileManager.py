import pygame
import os
import json
from factory import garage,maps
class SaveManager():
    def __init__(self,file_name='saves.json',save_folder_name='save_files'):
        self.save_file = f'{save_folder_name}/{file_name}'
        if not os.path.exists(save_folder_name):
            os.makedirs(save_folder_name, exist_ok=True)
        if not os.path.isfile(self.save_file):
            open(f"{save_folder_name}/{file_name}", 'w').close()
        self.save_on_first_run()
    def savedata(self,data):
        if self.has_data():
            with open(self.save_file, 'r') as save_file:
                prev_data = json.load(save_file)
        else:
            prev_data = {}
        prev_data.update(data)


        if not self.is_same_data(data):
            with open(self.save_file, 'w') as save_file:
                    json.dump(prev_data,save_file,indent=4)
        else:

            return
            
    def is_same_data(self,data_given):
        if os.path.getsize(self.save_file) == 0:
            prev_data = {}
        else:
            with open(self.save_file, 'r') as save_file:
                prev_data = json.load(save_file)
                if prev_data != data_given:
                    return False
                else:
                    return True
                
    def load_data(self):
        if self.has_data():
            with open(self.save_file, 'r') as save_file:
                the_data = json.load(save_file)
            return the_data
        else:
            return {}
    def has_data(self):
        if os.path.getsize(self.save_file) > 0:
            return True
        
    def save_on_first_run(self):
        ## SAVES THE CARS
        cars = garage.keys()
        save_data = self.load_data()
        try:
            if cars == save_data['car_state']:
                print('all cars ok')
                return
        except KeyError:
            pass
        if 'car_state' not in save_data:
            print('no cars state')
            save_data['car_state'] = {}
        updated = False
        for car in cars:
            if car not in save_data['car_state']:
                save_data['car_state'][car] = False
                if car == 'aston_martin':
                    save_data['car_state']['aston_martin'] = True
                updated = True
                print(f'added {car}: {save_data['car_state'][car]}')
        if updated:
            self.savedata(save_data)
        ## SAVES the MAPS   
        the_maps = maps.keys()
        try: 
            if the_maps == save_data['map_states']:
                print('all maps in bro')
        except KeyError:
            pass
        if 'map_states' not in save_data:
            print('map_state not ok ')
            save_data['map_states'] = {}
        updated_map = False
        for the_map in the_maps:
            if the_map not in save_data['map_states']:
                save_data['map_states'][the_map] = False

                if the_map == 'raceway' or 'freeroam':
                    save_data['map_states']['raceway'] = True
                    save_data['map_states']['freeroam'] = True
                updated_map = True
                print(f'added {the_map}: {save_data['map_states'][the_map]}')
        if updated_map:
            self.savedata(save_data)


savemanager = SaveManager()