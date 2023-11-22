import pygame
import pymunk
import images
import maps
from pygame.locals import *
from pygame.color import *

def title_screen():
    game_pause = True
    while title_score: #Initalise score screen
        screen.fill(pygame.Color("black"))

        screen.blit(score_screen_background, (0, 0))
        
        menu_rect = pygame.Rect(350, 200, 250,50)
        start_rect = pygame.Rect(350, 300, 250,50)
        
        pygame.draw.rect(screen, pygame.Color("blue"), menu_rect, border_radius=10)
        text_surface = my_font.render('Main Menu', False, (0, 0, 0))
        
        pygame.draw.rect(screen, pygame.Color("red"), start_rect, border_radius=10)
        text_surface2 = my_font.render('Restart', False, (0, 0, 0))
        
        screen.blit(text_surface, (menu_rect.x, menu_rect.y))
        screen.blit(text_surface2, (start_rect.x, start_rect.y))
        
        y = 100
        for item,i  in zip(tanks_list, range(len(tanks_list))):
            menu.text_creator(screen, 50, f"Player {i+1}: {score_dic[item]}", pygame.Color("white"),(100,100+y))
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
                    score_dic = {}
                    tanks_list = []
                    menu.welcome_screen()
                    

                if start_rect_py.collidepoint(mouse_pos):
                    title_score = False
                    running = False
                    screen = pygame.display.set_mode(current_map.rect().size)  
                    reset_game()
                    running = True

    while game_pause:
        for event in pygame.event.get():
        if event.type == pygame.QUIT:
        game_pause = False
        # Handle any clean-up or exit logic here

        # Check for button clicks and handle them
        if event.type == pygame.MOUSEBUTTONDOWN:
        if restart_button.collidepoint(event.pos):
            reset_game()
            running = False  # Exit title screen and start the game
        elif main_menu_button.collidepoint(event.pos):
            # Handle returning to the main menu

        # Render the title screen elements here
        screen.fill(pygame.Color("black"))
        # Render buttons, text, etc.

        pygame.display.flip()
        clock.tick(60)  # Control the frame rate

        # Call this function when needed, e.g., after a game round ends
        # title_screen()
