from pprint import pprint


base_width,base_height = 130,50
aston_acceleration = 350
glinton_acceleration = 375
esquire_acceleration = 425
lamborghini_acceleration = 500
pony_acceleration = 450
mustang_acceleration = 550
premer_acceleration = 400
mclaren_acceleration = 600
bmw_acceleration = 1000
neon_blue_acceleration = 900
thrill_acceleration = 800

def get_car(name,extension = 'png'):
    return f"cars/{name}.{extension}"



garage = {
    "aston_martin": {
        'width': base_width,
        'height': base_height,
        'image': "cars/aston_martin.png",
        'acceleration': aston_acceleration,
        'max_speed': aston_acceleration * 5,  # 1750
        'brake': 4,
        'handling': 0.5,
        'price': 0
        
    },

    "glinton":{
        'width': base_width,
        'height': base_height,
        'image': "cars/glinton.png",
        'acceleration': glinton_acceleration,
        'max_speed': glinton_acceleration * 5,  # 1875
        'brake': 4.5,
        'handling': 0.5,
        'price': 3000
    },

    "esquire":{
        'width': base_width,
        'height': base_height,
        'image': "cars/esquire.png",
        'acceleration': esquire_acceleration,
        'max_speed': esquire_acceleration * 5,  # 2125
        'brake': 5,
        'handling': 0.5,
        'price': 6000
    },

    "lamborghini":{
        'width': base_width,
        'height': base_height,
        'image': "cars/lamborghini.png",
        'acceleration': lamborghini_acceleration,
        'max_speed': lamborghini_acceleration * 5,  # 2500
        'brake': 7.5,
        'handling': 0.55,
        'price': 100000,
    },

    "pony":{
        'width': base_width,
        'height': base_height,
        'image': "cars/pony.png",
        'acceleration': pony_acceleration,
        'max_speed': pony_acceleration * 5,  # 2250
        'brake': 7.5,
        'handling': 0.55,
        'price': 150000,
    },

    "premer":{
        'width': base_width,
        'height': base_height,
        'image': get_car('premer'),
        'acceleration': premer_acceleration,
        'max_speed': premer_acceleration * 5,  # 2500
        'brake': 10,
        'handling': 0.5,
        'price': 180000,
    },
    "thrill":{
            'width': base_width,
            'height': base_height,
            'image': "cars/thrill.png",
            'acceleration': thrill_acceleration,
            'max_speed': thrill_acceleration * 5,  
            'brake': 11,
            'handling': 0.6,
            'price': 190000
    },
    
        "mustang":{
        'width': base_width,
        'height': base_height,
        'image': "cars/mustang.png",
        'acceleration': mustang_acceleration,
        'max_speed': mustang_acceleration * 5,  
        'brake': 14,
        'handling': 0.4,
        'price': 200000
    },
    "mclaren":{
        'width': base_width,
        'height': base_height,
        'image': get_car('mclaren'),
        'acceleration': mclaren_acceleration,
        'max_speed': mclaren_acceleration * 5,  # 2500
        'brake': 16,
        'handling': 0.7,
        'price': 240000,
    },

    "neon blue":{
        'width': base_width,
        'height': base_height,
        'image': "cars/neon_blue.png",
        'acceleration': neon_blue_acceleration,
        'max_speed': neon_blue_acceleration * 5,  # 2500
        'brake': 15,
        'handling': 0.6,
        'price': 290000,
    },

    "BMW":{
        'width': base_width,
        'height': base_height,
        'image': "cars/bmw.png",
        'acceleration': bmw_acceleration,
        'max_speed': bmw_acceleration * 5,  # 2500
        'brake': 10,
        'handling': 0.8,
        'price': 300000,
    },
}


def get_map_data(name,extension= 'png',time=15):
    the_dict = {
        'map': f'maps/{name}/{name}.{extension}',
        'road': f'maps/{name}/{name}_road.{extension}',
        'thumbnail': f'maps/{name}/{name}_tn.{extension}',
        'time': time
    }
    return the_dict


maps = {
    "freeroam":{
        **get_map_data('freeroam',time=1000),
        'prize': 0,
    },

    'raceway': {
        **get_map_data('raceway',time=20),
        'prize': 3000
        
    },
    'desert':{
        **get_map_data('desert'),
        'prize': 5000
    },
    'phool':{
        **get_map_data('phool'),
        'prize': 10000
    },
    'elemental': {
        **get_map_data('elemental'),
        'prize': 4000
    },

    
    'blood_run': {
        **get_map_data('BloodRun'),
        'prize': 6000
    },
    'space':{
        **get_map_data('space'),
        'prize': 25000
    },
    'maze':{
        **get_map_data('Maze',time=30),
        'prize': 45000,
    },
    'bangladesh':{
        **get_map_data('bangladesh'),
        'prize':50000,
    },
    "multiend":{
        **get_map_data('multiend',time=150),
        'prize': 1000000,
    }

    # 'loop':{
    #     'map': 'maps/loop/loop.png',
    #     'road': 'maps/loop/loop_road.png',
    #     'thumbnail': 'maps/loop/loop.png'
    # },

    # 'river':{
    #     'map': 'maps/river/river.png',
    #     'road': 'maps/river/river_road.png',
    #     'thumbnail': 'maps/river/river.png',
    # },
    # 'city':{
    #     'map': 'maps/city/city.png',
    #     'road': 'maps\city\city_road.png',
    #     'thumbnail': 'maps/city/city.png',
    # },
    # 'village':{
    #     'map': 'maps/village/village.png',
    #     'road': 'maps/village/village_road.png',
    #     'thumbnail': 'maps/village/village_tn.jpg',
    # },
    # 'high_way':{
    #     'map': 'maps/high_way/high_way.png',
    #     'road': 'maps/high_way/high_way_road.png',
    #     'thumbnail':'maps/high_way/high_way_tn.jpg',
    # },
    # 'new_loop':{
    #     'map': 'maps/new_loop/new_loop.png',
    #     'road': 'maps/new_loop/new_loop_road.png',
    #     'thumbnail':'maps/new_loop/new_loop_tn.jpg',
    # },
    
}
pprint(maps['raceway'])