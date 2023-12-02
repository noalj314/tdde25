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
    score_font = pygame.font.SysFont('Arcade Classic', 50)
    title_score = True
    
    while title_score: #Initalise score screen
        screen.fill([255, 255, 255])    
        screen.blit(images.score,(0,0))
        
        y = 263
        for i in range(len(tanks_list)):
            menu.text_creator(screen, score_font, f"Player {i+1}", pygame.Color("black"),(280,100+y))
            menu.text_creator(screen, score_font, f"                                                      {tanks_list[i].score}", pygame.Color("green"),(280,100+y))
            y += 65
            
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                title_score = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                menu_rect = pygame.Rect(80, 880, 350,80)
                start_rect = pygame.Rect(600, 880, 350,80)
                if menu_rect.collidepoint(mouse_pos):
                    title_score = False
                    menu.welcome_screen(UI_WIDTH)
                    return [0,0,0,0,0,0]
                    
                if start_rect.collidepoint(mouse_pos):
                    title_score = False
                    running = False
                    screen = pygame.display.set_mode(current_map.rect().size+pymunk.Vec2d(UI_WIDTH*2, 0))
                    score_list = []
                    for t in tanks_list:
                        score_list.append(t.score)
                    return score_list
        pygame.display.flip() #Update screen