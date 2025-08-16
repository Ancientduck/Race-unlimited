
base_width,base_height = 160,60


aston_acceleration = 350
glinton_acceleration = 375
esquire_acceleration = 425
lamborghini_acceleration = 500
pony_acceleration = 450
bmw_acceleration = 500

garage = {
    "aston_martin": {
        'width': base_width,
        'height': base_height,
        'image': "cars/aston_martin.png",
        'acceleration': aston_acceleration,
        'max_speed': aston_acceleration * 5,  # 1750
        'brake': 4,
        'handling': 0.3
    },

    "glinton":{
        'width': base_width,
        'height': base_height,
        'image': "cars/glinton.png",
        'acceleration': glinton_acceleration,
        'max_speed': glinton_acceleration * 5,  # 1875
        'brake': 4.5,
        'handling': 0.3
    },

    "esquire":{
        'width': base_width,
        'height': base_height,
        'image': "cars/esquire.png",
        'acceleration': esquire_acceleration,
        'max_speed': esquire_acceleration * 5,  # 2125
        'brake': 5,
        'handling': 0.3
    },

    "lamborghini":{
        'width': base_width,
        'height': base_height,
        'image': "cars/lamborghini.png",
        'acceleration': lamborghini_acceleration,
        'max_speed': lamborghini_acceleration * 5,  # 2500
        'brake': 7.5,
        'handling': 0.35
    },

    "pony":{
        'width': base_width,
        'height': base_height,
        'image': "cars/pony.png",
        'acceleration': pony_acceleration,
        'max_speed': pony_acceleration * 5,  # 2250
        'brake': 7.5,
        'handling': 0.35
    },

    "BMW":{
        'width': base_width,
        'height': base_height,
        'image': "cars/bmw.png",
        'acceleration': bmw_acceleration,
        'max_speed': bmw_acceleration * 5,  # 2500
        'brake': 10,
        'handling': 0.4
    },
}

maps = {
    "test":{
        'map': 'maps/test/test.png',
        'road': 'maps/test/test_road.png',
    },

    'loop':{
        'map': 'maps/loop/loop.png',
        'road': 'maps/loop/loop_road.png',
    },

    'river':{
        'map': 'maps/river/river.png',
        'road': 'maps/river/river_road.png',
        
    },
    'city':{
        'map': 'maps/city/city.png',
        'road': 'maps\city\city_road.png',
        
    },
    'village':{
        'map': 'maps/village/village.png',
        'road': 'maps/village/village_road.png',
    
    },
    'high_way':{
        'map': 'maps/high_way/high_way.png',
        'road': 'maps/high_way/high_way_road.png',
    
    },

}