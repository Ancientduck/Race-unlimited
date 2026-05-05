import time
import random
class ScreenShake:
    def __init__(self):
        self.shakes = []  # Queue of shakes
        self.object_shakes = []
        self.offset_x = 0
        self.offset_y = 0
        self.object_x,self.object_y = 0,0

    def apply_shake(self, duration, intensity):
        self.shakes.append({
            'end_time': time.time() + duration,
            'intensity': intensity
        })
        
    def make(self):

        total_offset_x = 0
        total_offset_y = 0   

        # Remove shakes that have ended
        self.shakes = [shake for shake in self.shakes if time.time() < shake['end_time']]

        # Apply all active shakes (stack intensities)
        for shake in self.shakes:
            total_offset_x += random.randint(-shake['intensity'], shake['intensity'])
            total_offset_y += random.randint(-shake['intensity'], shake['intensity'])

        # Set final offset
        self.offset_x = total_offset_x
        self.offset_y = total_offset_y
        return self.offset_x,self.offset_y
    
    def object_shake(self,duration,intensity):
        self.object_shakes.append({
            'end_time': time.time() + duration,
            'intensity': intensity
        })

    def object_make(self):
        total_offset_x = 0
        total_offset_y = 0   

        # Remove shakes that have ended
        self.object_shakes = [shake for shake in self.object_shakes if time.time() < shake['end_time']]

        # Apply all active shakes (stack intensities)
        for shake in self.object_shakes:
            total_offset_x += random.randint(-shake['intensity'], shake['intensity'])
            total_offset_y += random.randint(-shake['intensity'], shake['intensity'])

        # Set final offset
        self.object_x = total_offset_x
        self.object_x = total_offset_y
        return self.object_x,self.object_x

screen_shake = ScreenShake()