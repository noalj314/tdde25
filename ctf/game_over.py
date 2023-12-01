import pygame
import pymunk
import images
import maps
import menu
from pygame.locals import *
from pygame.color import *
multiplayer = None



def game_over(current_map, tanks_list, UI_WIDTH):
    screen = pygame.display.set_mode((1024,1024))
    my_font = pygame.font.SysFont('Comic Sans MS', 20)
    title_score = True
    
    while title_score: #Initalise score screen
        screen.fill([255, 255, 255])    
        screen.blit(images.score,(0,0))

        
        menu_rect = pygame.Rect(350, 200, 250,50)
        start_rect = pygame.Rect(350, 300, 250,50)
        
        pygame.draw.rect(screen, pygame.Color("blue"), menu_rect, border_radius=10)
        text_surface = my_font.render('Main Menu', False, (0, 0, 0))
        
        pygame.draw.rect(screen, pygame.Color("red"), start_rect, border_radius=10)
        text_surface2 = my_font.render('Continue', False, (0, 0, 0))
        
        screen.blit(text_surface, (menu_rect.x, menu_rect.y))
        screen.blit(text_surface2, (start_rect.x, start_rect.y))
        

        
        y = 100
        for i in range(len(tanks_list)):
            menu.text_creator(screen, menu.menu_font, f"Player {i+1}: {tanks_list[i].score}", pygame.Color("white"),(100,100+y))
            y += 100
            
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                title_score = False
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                map_y = 650
                
                menu_rect_py = pygame.Rect(350, 200, 250,50)
                start_rect_py = pygame.Rect(350, 300, 250,50)
                if menu_rect_py.collidepoint(mouse_pos):
                    title_score = False
                    running = False
                    menu.welcome_screen(UI_WIDTH)
                    return [0,0,0,0,0,0]
                    
                if start_rect_py.collidepoint(mouse_pos):
                    title_score = False
                    running = False
                    screen = pygame.display.set_mode(current_map.rect().size+pymunk.Vec2d(UI_WIDTH*2, 0))
                    score_list = []
                    for t in tanks_list:
                        score_list.append(t.score)
                    return score_list
        pygame.display.flip() #Update screen