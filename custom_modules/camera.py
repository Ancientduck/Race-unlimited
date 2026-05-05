
def camera(x,y,screen_size,map_size):

    screen_width,screen_height = screen_size

    map_width,map_height = map_size

    camera_width = screen_width//2
    camera_height = screen_height//2


    camera_x = x - camera_width
    camera_y = y - camera_height


    #clamp the boundries
    camera_x = max(0,min(camera_x,map_width-screen_width))
    camera_y = max(0,min(camera_y,map_height - screen_height))
    
    return camera_x,camera_y