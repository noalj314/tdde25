import pygame
import pymunk
import images
import maps
import sys
import menu
from pygame.locals import *
from pygame.color import *
multiplayer = None
scale_fctr = 1 if '--big' in sys.argv else 0.5


def game_over(current_map, tanks_list, UI_WIDTH):
    """A screen that gets called when a player or ai wins"""
    screen = pygame.display.set_mode((1024 * scale_fctr, 1024 * scale_fctr))
    score_font = pygame.font.SysFont('Arcade Classic', int(50 * scale_fctr))
    title_score = True

    while title_score:  # Initalise score screen
        screen.fill([255, 255, 255])
        screen.blit((pygame.transform.scale(images.score, (1024 * scale_fctr, 1024 * scale_fctr))), (0, 0))

        y = (262)
        for i in range(len(tanks_list)):
            menu.text_creator(screen, score_font, f"Player {i + 1}", pygame.Color("black"), (280 * scale_fctr, (100 + y) * scale_fctr))
            menu.text_creator(screen, score_font, f"                                                 {tanks_list[i].score}", pygame.Color("green"), (scale_fctr * 280, scale_fctr * (110 + y)))
            y += 65

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                title_score = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                menu_rect = pygame.Rect(80 * scale_fctr, 880 * scale_fctr, 350 * scale_fctr, 80 * scale_fctr)
                start_rect = pygame.Rect(600 * scale_fctr, 880 * scale_fctr, 350 * scale_fctr, 80 * scale_fctr)
                if menu_rect.collidepoint(mouse_pos):
                    title_score = False
                    menu.welcome_screen(UI_WIDTH)
                    return [0, 0, 0, 0, 0, 0]

                if start_rect.collidepoint(mouse_pos):
                    title_score = False
                    running = False
                    screen = pygame.display.set_mode(current_map.rect().size + pymunk.Vec2d(UI_WIDTH * 2, 0))
                    score_list = []
                    for t in tanks_list:
                        score_list.append(t.score)
                    return score_list
        pygame.display.flip()  # Update screen
