import pygame
import pymunk
import images
import maps
from pygame.locals import *
from pygame.color import *
multiplayer = None

screen = pygame.display.set_mode((1024,1024))


def text_creator(screen, size, text, colour, pos):
    font = pygame.font.Font(None, size)
    text_create = font.render(text, True, colour)
    screen.blit(text_create, pos)

def map_options(screen, ma, pos):
    text_creator(screen, 40, ma, pygame.Color('white'), pos)

def welcome_screen(ui_width):
    global multiplayer,current_map, screen
    not_playing = True
    current_map = None
    while not_playing:
        screen.fill([255, 255, 255])
        
        screen.blit(images.menu,(0,0))
        
        singleplayer_rect = pygame.Rect(630, 650, 250,50)
        multiplayer_rect = pygame.Rect(630, 760, 250,50)
        
        pygame.draw.rect(screen, pygame.Color("blue"), singleplayer_rect, border_radius=10)
        pygame.draw.rect(screen, pygame.Color("red"), multiplayer_rect, border_radius=10)
        text_creator(screen, 50,"Singleplayer", pygame.Color("white"),(650,660))
        text_creator(screen, 50,"Multiplayer", pygame.Color("white"),(650,770))
        
        map_options(screen, maps.maps_list[0], (185, 650 + 40)) #creates text
        thumbnail = maps.maps_list_no_str[0].gen_thumbnail() # generates thumbnail
        screen.blit(thumbnail, (85, 650))

        map_options(screen, maps.maps_list[1], (185, 760 + 40)) #creates text
        thumbnail = maps.maps_list_no_str[1].gen_thumbnail() # generates thumbnail
        screen.blit(thumbnail, (85, 760))

        map_options(screen, maps.maps_list[2], (380, 650 + 40)) #creates text
        thumbnail = maps.maps_list_no_str[2].gen_thumbnail() # generates thumbnail
        screen.blit(thumbnail, (280, 650))

        map_options(screen, maps.maps_list[3], (380, 760 + 40)) #creates text
        thumbnail = maps.maps_list_no_str[3].gen_thumbnail() # generates thumbnail
        screen.blit(thumbnail, (280, 760))
        
        map_y_positions = [650, 760, 650, 760]
        map_x_positions = [85,85, 300, 300]
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
                not_playing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                map_y = 650
                if multiplayer_rect.collidepoint(mouse_pos):
                    multiplayer = True
                if singleplayer_rect.collidepoint(mouse_pos):
                    multiplayer = False
                for ma, x_pos, y_pos in zip(maps.maps_list_no_str, map_x_positions, map_y_positions):
                    map_rect = pygame.Rect(x_pos, y_pos, 100,100)
                    if map_rect.collidepoint(mouse_pos):
                        not_playing = False
                        current_map = ma 
        if multiplayer:
            text_creator(screen, 50, "Multiplayer Activated", pygame.Color("red"), (575, 820))
        if not multiplayer:
            text_creator(screen, 50, "Singleplayer Activated", pygame.Color("blue"), (565, 710))
                    
        pygame.display.flip()
    
    screen = pygame.display.set_mode(current_map.rect().size + pymunk.Vec2d(ui_width*2,0))

