import cv2
import numpy as np
def get_map_data(name,extension= 'png'):
    the_dict = {
        'map': f'maps/{name}/{name}.{extension}',
        'road': f'maps/{name}/{name}_road.{extension}',
        'thumbnail': f'maps/{name}/{name}_tn.{extension}',
    }
    return the_dict
name = 'BloodRun'
the_map = get_map_data(name)
print(the_map)
im = np.load('maps\BloodRun\BloodRun.npy')       # decode the heavy PNG
print(im.shape)