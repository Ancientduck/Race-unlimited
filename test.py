import pygame
pygame.init()

screen = pygame.display.set_mode((700,700))
pygame.display.set_caption("Game")

speed = 20
x = 200
y = 600


def game_map():

    global rect_one
    surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    rect_one = pygame.draw.rect(surface, (0, 0, 255), (0, 0, 50, 50)) 

    global rect_two
    surface_one = pygame.Surface((80, 80), pygame.SRCALPHA)
    rect_two = pygame.draw.rect(surface_one, (255, 255, 255), (0, 0, 50, 50)) 

    tileX = 0
    tileY = 0

    global tile_list
    tile_list = []
    map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,1,0,1,0,0,0,0,0,1,1,0,0,0,1,0,1,0,0,0,0,0,1],
            [1,0,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,0,1,1,1,0,1],
            [1,0,0,0,1,1,1,0,0,0,0,0,1,1,0,0,0,1,1,1,0,0,0,0,0,1],
            [1,0,1,0,0,0,0,0,1,1,1,0,1,1,0,1,0,1,1,1,0,1,0,0,0,1],
            [1,0,1,0,1,1,1,0,1,0,0,0,1,1,0,1,0,1,0,0,0,1,1,1,0,1],
            [1,0,1,0,1,0,0,0,1,1,1,0,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
            [1,0,1,0,1,1,1,0,1,0,1,0,1,1,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]

    for y, row in enumerate(map):
        tileX = 0
        for x, cell in enumerate(row):
            image = surface if cell == 1 else surface_one
            screen.blit(image, [x*50, y*50]) 
            tile_list.append(rect_one)
    pygame.display.update() 


def player():
    player = pygame.draw.rect(screen, (255,0,0), (x, y, 20, 20))   

    for i in tile_list:
        if player.colliderect(i):
            print("hello")

loop = True

while loop:
    pygame.time.delay(100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False

    #player controls
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_UP]:
        y -= speed
    if keys[pygame.K_DOWN]:
        y += speed

    screen.fill((255,255,255))
    game_map()
    player()
    pygame.display.update()


pygame.quit()
