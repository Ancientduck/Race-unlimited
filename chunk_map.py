import os
import threading
import queue
import math
import pygame as pg
from PIL import Image as PILImage

chunk_size = 512
class ChunkMap():
    def __init__(self,map_path,zoom,chunk_dir=None):
        raw = PILImage.open(map_path)
        raw_w,raw_h = raw.size
        raw.close()

        self.raw_map_size = (raw_w,raw_h)
        self.map_width = int(raw_w*zoom)
        self.map_height = int(raw_h*zoom)

        self.cols = math.ceil(self.map_width/chunk_size)
        self.rows = math.ceil(self.map_height/chunk_size)
        
        if chunk_dir is None:
            base = os.path.splitext(os.path.basename(map_path))[0]
            chunk_dir = f"temp_files/chunks_{base}"
        self.chunk_dir = chunk_dir


        self.loading_queue = queue.Queue()
        self.loading_threads = []
        self.max_threads = 4
        
        for _ in range(self.max_threads):
            t = threading.Thread(target=self.chunk_loader_thread,daemon=True)
            t.start()
            self.loading_threads.append(t)


        self.loaded_chunks = {}
        #self.pre_loaded_chunks = {}


        if not os.path.exists(chunk_dir):
            print('first launch, slicing the map')
            self.preprocess(map_path)
        else:
            print('not first launch, loading the map from disk')

        # for row in range(self.rows):
        #     for col in range(self.cols):
        #         path = f"{self.chunk_dir}/chunk_{col}_{row}.png"
        #         img = pg.image.load(path).convert()
        #         self.pre_loaded_chunks[(col, row)] = img

        

    def preprocess(self,map_path):
        os.makedirs(self.chunk_dir)
        img = PILImage.open(map_path)
        scaled = img.resize((self.map_width,self.map_height),PILImage.LANCZOS)
        img.close()

        for row in range(self.rows):
            for col in range(self.cols):
                x = col*chunk_size
                y = row*chunk_size
                chunk = scaled.crop((
                    x,y,
                    min(x+chunk_size,self.map_width),
                    min(y+chunk_size,self.map_height)

                ))
                chunk = chunk.convert('RGB')
                chunk.save(f"{self.chunk_dir}/chunk_{col}_{row}.png")

        scaled.close()

    # def load_chunk(self, col, row):
    #     key = (col, row)

    #     if key not in self.loaded_chunks:
    #         if key in self.pre_loaded_chunks:
    #             self.loaded_chunks[key] = self.pre_loaded_chunks[key]
    
    def request_chunk(self,col,row):
        key = (col,row)
        if key not in self.loaded_chunks:
            if key not in list(self.loading_queue.queue):
                self.loading_queue.put(key)
    
    def chunk_loader_thread(self):
        while True:
            key = self.loading_queue.get()
            if key is None:
                break
            col,row = key
            path = f"{self.chunk_dir}/chunk_{col}_{row}.png"
            if os.path.exists(path):
                img = pg.image.load(path).convert()
                self.loaded_chunks[key] = img
            self.loading_queue.task_done()


    def update(self,camera_x,camera_y,screen_w,screen_h,load_radius=1):
        col_min = max(0,camera_x//chunk_size - load_radius)
        col_max = min(self.cols-1,(camera_x + screen_w)//chunk_size+load_radius)
        
        row_min = max(0,camera_y//chunk_size-load_radius)
        row_max = min(self.rows-1,(camera_y+screen_h)//chunk_size+load_radius)

        needed = set()
        for row in range(int(row_min),int(row_max)+1):
            for col in range(int(col_min),int(col_max) + 1):
                needed.add((col,row))
                self.request_chunk(col,row)

        for key in list(self.loaded_chunks):
            if key not in needed:
                del self.loaded_chunks[key]
        
    
    def draw(self,surface,camera_x,camera_y,offset_x=0,offset_y = 0):
        for (col,row), chunk in self.loaded_chunks.items():
            x=col*chunk_size - camera_x + offset_x
            y= row*chunk_size - camera_y + offset_y
            surface.blit(chunk,(x,y))

    def stop_threads(self):
        for _ in self.loading_threads:
            self.loading_queue.put(None)
        for t in self.loading_threads:
            t.join()
        
    def get_rect(self):
        return pg.Rect(0,0,self.map_width,self.map_height)
