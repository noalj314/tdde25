import pygame
import pymunk
import images
import maps
import sys
from pygame.locals import *
from pygame.color import *
multiplayer = None

scale_fctr = 1 if '--big' in sys.argv else 0.5
screen = pygame.display.set_mode((1024 * scale_fctr, 1024 * scale_fctr))
menu_font = pygame.font.Font(None, int(float(50) * scale_fctr))


def text_creator(screen, font, text, colour, pos):
    """Creates text and blits it on the screen"""
    text_create = font.render(text, True, colour)
    screen.blit(text_create, pos)


def map_options(screen, ma, pos):
    """Create text for the maps"""
    text_creator(screen, menu_font, ma, pygame.Color('white'), pos)


def scale_rect(x, y, width, height, scale_factor):
    """Scaling a rectangle"""
    return pygame.Rect(x * scale_factor, y * scale_factor, width * scale_factor, height * scale_factor)


def welcome_screen(ui_width):
    """ The main function for the welcome screen. """
    global multiplayer, current_map, screen
    not_playing = True
    current_map = None
    while not_playing:
        screen.fill([255, 255, 255])
        screen.blit(pygame.transform.scale(images.menu, (1024 * scale_fctr, 1024 * scale_fctr)), (0, 0))
        # Create multiplayer and singleplayer rectangles
        singleplayer_rect = scale_rect(630, 650, 250, 50, scale_fctr)
        multiplayer_rect = scale_rect(630, 760, 250, 50, scale_fctr)
        pygame.draw.rect(screen, pygame.Color("blue"), singleplayer_rect, border_radius=10)
        pygame.draw.rect(screen, pygame.Color("red"), multiplayer_rect, border_radius=10)
        text_creator(screen, menu_font, "Singleplayer", pygame.Color("white"), (650 * scale_fctr, 660 * scale_fctr))
        text_creator(screen, menu_font, "Multiplayer", pygame.Color("white"), (650 * scale_fctr, 770 * scale_fctr))

        # Create all the map text and thumbnails
        map_options(screen, maps.maps_list[0], (185 * scale_fctr, (650 + 40) * scale_fctr))  # creates text
        thumbnail = maps.maps_list_no_str[0].gen_thumbnail((100 * scale_fctr, 100 * scale_fctr))  # generates thumbnail
        screen.blit(thumbnail, ((85) * scale_fctr, scale_fctr * (650)))

        map_options(screen, maps.maps_list[1], (185 * scale_fctr, scale_fctr * (760 + 40)))  # creates text
        thumbnail = maps.maps_list_no_str[1].gen_thumbnail((100 * scale_fctr, 100 * scale_fctr))  # generates thumbnail
        screen.blit(thumbnail, (85 * scale_fctr, 760 * scale_fctr))

        map_options(screen, maps.maps_list[2], (380 * scale_fctr, scale_fctr * (650 + 40)))  # creates text
        thumbnail = maps.maps_list_no_str[2].gen_thumbnail((100 * scale_fctr, 100 * scale_fctr))  # generates thumbnail
        screen.blit(thumbnail, (280 * scale_fctr, 650 * scale_fctr))

        map_options(screen, maps.maps_list[3], (380 * scale_fctr, scale_fctr * (760 + 40)))  # creates text
        thumbnail = maps.maps_list_no_str[3].gen_thumbnail((100 * scale_fctr, 100 * scale_fctr))  # generates thumbnail
        screen.blit(thumbnail, (280 * scale_fctr, 760 * scale_fctr))

        map_y_positions = [650 * scale_fctr, 760 * scale_fctr, 650 * scale_fctr, 760 * scale_fctr]
        map_x_positions = [85 * scale_fctr, 85 * scale_fctr, 300 * scale_fctr, 300 * scale_fctr]
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                not_playing = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if multiplayer_rect.collidepoint(mouse_pos):
                    multiplayer = True
                if singleplayer_rect.collidepoint(mouse_pos):
                    multiplayer = False
                for ma, x_pos, y_pos in zip(maps.maps_list_no_str, map_x_positions, map_y_positions):
                    map_rect = pygame.Rect(x_pos, y_pos, 100 * scale_fctr, 100 * scale_fctr)
                    if map_rect.collidepoint(mouse_pos):
                        not_playing = False
                        current_map = ma
        if multiplayer:
            text_creator(screen, menu_font, "Multiplayer Activated", pygame.Color("red"), (575 * scale_fctr, 820 * scale_fctr))
        if not multiplayer:
            text_creator(screen, menu_font, "Singleplayer Activated", pygame.Color("blue"), (565 * scale_fctr, 710 * scale_fctr))

        pygame.display.flip()

    screen = pygame.display.set_mode(current_map.rect().size + pymunk.Vec2d(ui_width * 2, 0))
