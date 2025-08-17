import math
import pygame as pg
from kill_bug import debug


def get_offset(player_x,player_y,target_x,target_y):
    offset = ((player_x - target_x),(player_y-target_y))
    return offset

def get_around_points(rect,angle,original_image):
    # Half dimensions
    # Car's corners before rotation (relative to center)
    half_width = original_image.get_width()/2
    half_height = original_image.get_height()/2
    center_x,center_y = rect.centerx,rect.centery


    points = [
        (center_x - half_width, center_y - half_height),  # Top-left
        (center_x + half_width, center_y - half_height),  # Top-right  
        (center_x + half_width, center_y + half_height),  # Bottom-right
        (center_x - half_width, center_y + half_height),  # Bottom-left
       # (center_x, center_y),                             # Center
       # (center_x, center_y - half_height),               # (top middle)
       # (center_x, center_y + half_height),               # (bottom middle)
       # (center_x - half_width, center_y),                # Left-center
       # (center_x + half_width, center_y),                # Right-center
    ]

    rad = math.radians(-angle)
    cos_angle = math.cos(rad)
    sin_angle = math.sin(rad)
    
    rotated_points = []
    
    for point_x, point_y in points:
        # Convert to relative coordinates (offset from center)
        relative_x = point_x - center_x #// treat car center as the 0,0 
        relative_y = point_y - center_y  ##?? MAKE THE CAR'S CENTER 0,0
        
        # Apply rotation matrix to the relative coordinates
        rotated_x = relative_x * cos_angle - relative_y * sin_angle
        rotated_y = relative_x * sin_angle + relative_y * cos_angle
        
        # Translate back to world position
        world_x = center_x + rotated_x
        world_y = center_y + rotated_y
        
        rotated_points.append((world_x, world_y))
       # print(relative_x,relative_y)

    return rotated_points

class Collision_detect:
    
    
    def detect_by_object(self,player_rect,player_mask,target_rect,target_mask):
        player = player_rect
        player_mask = player_mask
        target = target_rect
        target_mask = target_mask

        offset = get_offset(player.x,player.y,target.x,target.y)
        if player.colliderect(target):
            print('collision_rect')
            if player_mask.overlap(target_mask,offset):
                print('fuck you')


    
    def detect_by_color(self, rect,original_image, the_map,angle,target_color):
                
        points  = get_around_points(rect,angle,original_image)
        

            
        for point in points:
            check_x,check_y = int(point[0]),int(point[1])
            

            if (0 <= check_x < the_map.get_width() and
                0 <= check_y < the_map.get_height()):
                pixel_color = the_map.get_at((check_x, check_y))[:3]
                if pixel_color == target_color:
                    points = check_x,check_y
                    return True,points  # found target color

        # No point matched
        return False,None
        

    def push(self,x,y,angle,rect,velocity, dt, power,collision_points):

        car_center = pg.math.Vector2(rect.center)
        collision_pos = pg.math.Vector2(collision_points)
    
        vel = velocity #vector
        collision_direction = car_center - collision_pos
        direction = vel.normalize()
        if collision_direction.length() > 0:
            collision_direction = collision_direction.normalize()

            
        x += collision_direction.x *power*dt  
        y += collision_direction.y *power*dt
            

        v_in_wall = vel.project(collision_direction)
        
        vel  -= v_in_wall*0.1


        angle_should_be = -math.degrees(math.atan2(vel.y,vel.x))
        angle_diff = (angle_should_be - angle + 180)%360 - 180

#        if direction.length() < 0:
        if angle_diff > 5:
            angle_diff = 5
        elif angle_diff < -5:
            angle_diff = -5

        if angle_diff > -3 and angle_diff < 3:
            angle_diff = 0
       # debug.debug_on_screen(angle_diff)
       # print(f'angle_should be : {angle_should_be}, angle_diff : {angle_diff}')

        angle += angle_diff * 0.6
        
        return x,y,angle, vel

collision_check = Collision_detect()
