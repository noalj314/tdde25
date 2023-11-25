""" Main file for the game.
"""
# -- Import relevant libraries
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import sys



# ----- Initialisation ----- #


# -- Initialise the display
pygame.init()
screen = pygame.display.set_mode((800,600))
ui_screen = pygame.display.set_mode((800,600))
UI_WIDTH = 200
control_mode = "turn"


# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the font
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 20)


# -- Import from the ctf framework
import ai
import images
import gameobjects
import maps
import sounds
import menu

 # -- Constants
multiplayer = None
 

    # -- Variables
    #   Define the current level


def main_game(score=[]):
    
    # -- Initialise the physics
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    space.damping = 0.1  # Adds friction to the ground for all objects

    #-- Initialise global variables
    global multiplayer, current_map, screen, control_mode
    
    # -- List of all game objects
    current_map = menu.current_map
    multiplayer = menu.multiplayer
    screen = menu.screen
    game_objects_list = []
    tanks_list = []
    bullet_list = []
    ai_list = []

    def remove_shape(space, shape, shape2=None):
        """Removes shapes and bodies from the space"""
        space.remove(shape, shape.body)
        if shape2:
            space.remove(shape2,shape2.body)


    def remove_from_list(lst, obj):
        """Remove an object from its list."""
        lst.remove(obj)


    def reset_tank(tank):
        """Reset the tanks position to its starting position."""
        tank.body.angle = tank.start_orientation
        tank.body.position = tank.start_position.x, tank.start_position.y
        tank.respawn = 0


    def drop_flag(tank,flag):
        """Drops the flag at the tanks current posistion"""
        gameobjects.Flag(tank.body.position.x, tank.body.position.y)
        tank.flag = None
        flag.is_on_tank = False
        return flag


    def hit(item, bullet):
        """Update the dictionary hit_points if a tank or wood wall is hit"""
        item.hp -= bullet.damage
        if item.hp <= 0:
            if isinstance(item, gameobjects.Tank):
                if item.flag:
                    drop_flag(item, flag)
                reset_tank(item)
                item.hp = item.max_hp
            else:
                remove_shape(space, item.shape)
                try:
                    remove_from_list(game_objects_list, item)
                except ValueError:
                    print("Unable to remove box from game_objects_list")
            return True
        else:
            return False


    def collision_bullet_wood(arb, space, data):
        """Triggered when bullet and wooden box collide, removing both from the space and their lists."""
        bullet = arb.shapes[0].parent
        remove_shape(space,arb.shapes[0])
        sounds.explosion_sound.play()
        try:
            remove_from_list(bullet_list,arb.shapes[0].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit wood")
        return hit(arb.shapes[1].parent, bullet)
        

    def collision_bullet_wall(arb, space, data):
        """Triggered when bullet and wall collide, removing the bullet from the space and bullet_list."""
        remove_shape(space, arb.shapes[0])
        sounds.explosion_sound.play()
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit wall")
        return True


    def collision_bullet_tank(arb, space, data):
        """Triggered when bullet and tank collide, removing the bullet from the space and bullet_list and resetting the position of the tank."""
        tank = arb.shapes[1].parent
        bullet = arb.shapes[0].parent
        remove_shape(space, arb.shapes[0])
        sounds.explosion_sound.play()
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit wall")
        if gameobjects.Tank.ability_to_die(tank):
            return hit(tank, bullet)
        return True


    def collision_bullet_bullet(arb, space, data):
        """Triggered when bullet and another bullet collide, removing the bullets from the space and bullet_list."""
        remove_shape(space, arb.shapes[0],arb.shapes[1])
        sounds.explosion_sound.play()
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
            remove_from_list(bullet_list, arb.shapes[1].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit other bullet")
        return True
    

    def collision_handler(space, object1, object2, collision_function):
        """Creates a CollisionHandler with two collision_types and a function which triggers on contact."""
        handle = space.add_collision_handler(object1, object2)
        handle.pre_solve = collision_function
        return handle

    b_w_handler = collision_handler(space, 4, 2, collision_bullet_wood)
    b_s_handler = collision_handler(space, 4, 1, collision_bullet_wall)
    b_m_handler = collision_handler(space, 4, 3, collision_bullet_wall)
    b_metal_handler = collision_handler(space, 4, 0, collision_bullet_wall)
    b_t_handler = collision_handler(space, 4, 5, collision_bullet_tank)
    b_b_handler = collision_handler(space, 4, 4, collision_bullet_bullet)
    

    def barrier(current_map, space):
        """Adds a barrier to prevent from going outside the screen"""
        static_body = space.static_body
        static_lines = [
            pymunk.Segment(static_body, (0, 0), (current_map.width, 0), 0.0),
            pymunk.Segment(static_body, (current_map.width, 0), (current_map.width, current_map.height), 0.0),
            pymunk.Segment(static_body, (0, 0), (0, current_map.height), 0.0),
            pymunk.Segment(static_body, (0, current_map.height), (current_map.width, current_map.height), 0.0),
        ]
        for line in static_lines:
            line.elasticity = 1
            line.friction = 0.9
        space.add(*static_lines)
    

    def create_background(screen, current_map, images):
        """Creates a plain background with grass and no objects"""
        background = pygame.Surface(screen.get_size())
        for y in range(0,  current_map.height):
            for x in range(0,  current_map.width):
                background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))
        return background
    

    def create_boxes():
        """Adds boxes to the map that acts as physical objects"""
        for x in range(0, current_map.width):
            for y in range(0,  current_map.height):
            # Get the type of boxes
                box_type = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
                if(box_type != 0):
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                    box = gameobjects.get_box_with_type(x, y, box_type, space)
                    box.shape.collision_type = box_type
                    game_objects_list.append(box)
                

    def create_tanks():
        """Creates tanks for every start position of the map"""
    # Loop over the starting poistion
        for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
            pos = current_map.start_positions[i]
        # Create the tank, images.tanks contains the image representing the tank
            tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
        #create the base at the same place as the tank
            base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])
        # Add the tank to the list of tanks
            tanks_list.append(tank)
        #Add collision_type for the tank
            tank.shape.collision_type = gameobjects.collision_types["tank"]
        # Add the base for the tank to the game_objects_list
            game_objects_list.append(base)
        # Create ai instances for each tank except the first
        
            tank.score = score[i]
        
            if multiplayer and i > 1:
                bot = ai.Ai(tanks_list[i], game_objects_list, tanks_list, bullet_list, space, current_map)
                ai_list.append(bot)
            elif not multiplayer and i > 0:
                bot = ai.Ai(tanks_list[i], game_objects_list, tanks_list, bullet_list, space, current_map)
                ai_list.append(bot)


    def create_flag():
        """Creates the flag in desired position"""
        flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
        game_objects_list.append(flag)
        return flag
    

    def update_ui():
        """Updates the visual menu with different stats such as score, fire rate..."""
        for i in range(len(tanks_list)):
            place = pygame.Rect((screen.get_size()[0]-UI_WIDTH)*(i%2), screen.get_size()[1]/int(len(tanks_list)/2)*(i//2), UI_WIDTH, screen.get_size()[1]/int(len(tanks_list)/2))
            colour = images.colours[i]
            
            pygame.draw.rect(screen, colour, place)
            
            text_surface = my_font.render('HP:', False, (0, 0, 0))
            screen.blit(text_surface, (place.x + 10, place.y + 10))
            for j in range(tanks_list[i].max_hp):
                rect = pygame.Rect(place.x + (j+4)*11, place.y + 14, 10, 20)
                pygame.draw.rect(screen, 0x000000, rect)
            for j in range(tanks_list[i].hp):
                rect = pygame.Rect(place.x + (j+4)*11, place.y + 14, 10, 20)
                pygame.draw.rect(screen, 0x00ff00, rect)
            menu.text_creator(screen, my_font, 'Score ' + str(tanks_list[i].score), 0x000000, (place.x + 10, place.y + 30))
            menu.text_creator(screen, my_font, 'Dmg ' + str(tanks_list[i].damage), 0x000000, (place.x + 10, place.y + 50))
            menu.text_creator(screen, my_font, 'Fire Rate ' + str(tanks_list[i].fire_rate) + "/s", 0x000000, (place.x + 10, place.y + 70))
            menu.text_creator(screen, my_font, 'Speed ' + str(tanks_list[i].max_speed), 0x000000, (place.x + 10, place.y + 90))
            menu.text_creator(screen, my_font, 'Bullet Speed ' + str(tanks_list[i].bullet_speed), 0x000000, (place.x + 10, place.y + 110))

    
    def object_functions():
        """Calls functions to initialise the objects"""
        barrier(current_map,space)
        create_boxes()
        create_tanks()
    
    object_functions()
    flag = create_flag()

    #  def reset_game():
    #     """A function that handles the reset ability of the game"""
    #     current_map = menu.current_map
    #     game_objects_list.clear()
    #     bullet_list.clear() 
    #     ai_list.clear()
    #     hit_points.clear()
    #     flag = create_flag()
        
    #     print(tanks_list)
    #     create_boxes()
    #     for tank in tanks_list:
    #         reset_tank(tank)


# ----- Main Loop -----#

# -- Control whether the game run
    running = True
    skip_update = 0
    skip_update_2 = 0
    variabel = 0
    score_screen_background = pygame.Surface(screen.get_size())
    score_screen_background.fill(pygame.Color("black"))
    
    pressed = {}
    #def orthogonal(u, d, l, r):
        
    while running:
        # -- Handle the events
        for event in pygame.event.get():
            #  Check if we receive a QUIT event (for instance, if the user press the
            #  close button of the wiendow) or if the user press the escape key.
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            #  Handles all events when keys are pressed and released
            if (event.type == KEYDOWN):
                if event.key == K_UP:
                    tanks_list[0].accelerate()
                elif (event.key == K_DOWN):
                    tanks_list[0].decelerate()
                elif (event.key == K_LEFT):
                    tanks_list[0].turn_left()
                elif (event.key == K_RIGHT):
                    tanks_list[0].turn_right()
                elif (event.key == K_RETURN) and tanks_list[0].ability_to_shoot():
                    tanks_list[0].shoot(space,bullet_list)
            if (event.type == KEYUP):
                if event.key == K_UP:
                    tanks_list[0].stop_moving()
                elif (event.key == K_DOWN):
                    tanks_list[0].stop_moving()
                elif (event.key == K_LEFT):
                    tanks_list[0].stop_turning()
                elif (event.key == K_RIGHT):
                    tanks_list[0].stop_turning()
            if multiplayer:
                if (event.type == KEYDOWN):
                    if event.key == K_w:
                        tanks_list[1].accelerate()
                    elif (event.key == K_s):
                        tanks_list[1].decelerate()
                    elif (event.key == K_a):
                        tanks_list[1].turn_left()
                    elif (event.key == K_d):
                        tanks_list[1].turn_right()
                    elif (event.key == K_SPACE) and tanks_list[1].ability_to_shoot():
                        tanks_list[1].shoot(space,bullet_list)
                if (event.type == KEYUP):
                    if event.key == K_w:
                        tanks_list[1].stop_moving()
                    elif (event.key == K_s):
                        tanks_list[1].stop_moving()
                    elif (event.key == K_a):
                        tanks_list[1].stop_turning()
                    elif (event.key == K_d):
                        tanks_list[1].stop_turning()
    
        # -- Update physics
        if skip_update == 0:
            #  Loop over all the game objects and update their speed in function of their
            #  acceleration.
            for obj in game_objects_list:
                obj.update()
            for obj in tanks_list:
                obj.update()
            for obj in bullet_list:
                obj.update()
            skip_update = 2
        else:
            skip_update -= 1
    
        #  Check collisions and update the objects position
        space.step(1 / gameobjects.FRAMERATE)
    
        #  Update object that depends on an other object position (for instance a flag)
        for obj in game_objects_list:
            obj.post_update()
        #  Try to grab the flag and then if it has the flag update the posistion of the tank
        for tank in tanks_list:
            tank.try_grab_flag(flag)
            tank.post_update()
            
            if tank.has_won():
                sounds.win_sound.play() # play win sound
                game_objects_list.remove(tank.flag)
                flag = create_flag()
                tank.flag = None
                tank.score += 1
                title_score = True
                screen = pygame.display.set_mode((1024,1024))
                while title_score: #Initalise score screen
                    screen.fill(pygame.Color("black"))
    
                    screen.blit(score_screen_background, (0, 0))
                    
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
                        menu.text_creator(screen, 50, f"Player {i+1}: {tanks_list[i].score}", pygame.Color("white"),(100,100+y))
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
                                
                            if start_rect_py.collidepoint(mouse_pos):
                                title_score = False
                                running = False
                                screen = pygame.display.set_mode(current_map.rect().size+pymunk.Vec2d(UI_WIDTH*2, 0))
                                score_list = []
                                for t in tanks_list:
                                    score_list.append(t.score)
                                main_game(score_list)
                                
                    pygame.display.flip()
    
                for item in tanks_list:
                    reset_tank(item)
                for i in range(len(tanks_list)):
                    print(f"Player {i+1}: {tanks_list[i].score}")
                for i in range(0, len(current_map.start_positions)):
                    if not multiplayer and i > 0:
                        ai_list[i-1] = ai.Ai(tanks_list[i], game_objects_list, tanks_list, bullet_list, space, current_map)
                    elif multiplayer and i > 1:
                        ai_list[i-2] = ai.Ai(tanks_list[i], game_objects_list, tanks_list, bullet_list, space, current_map)
    
        foreground = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
        background = create_background(screen, current_map, images)
    
        #  Update ai
        def bots():
            for ai in ai_list:
                ai.decide(background)
    
        # -- Update Display
        screen.blit(background, (UI_WIDTH, 0))
        # screen.blit(foreground, (0, 0))
        
        #  Update the display of the game objects on the screen
        def update_objects():
            for obj in game_objects_list:
                obj.update_screen(screen, UI_WIDTH)
            for tank in tanks_list:
                tank.update_screen(screen, UI_WIDTH)
            for bullet in bullet_list:
                bullet.update_screen(screen, UI_WIDTH)
        
        #  Call functions to update the display
        update_ui()
        update_objects()
        bots()

        #   Redisplay the entire screen (see double buffer technique)
        pygame.display.flip()
    
        #   Control the game framerate
        clock.tick(gameobjects.FRAMERATE)
    
menu.welcome_screen(UI_WIDTH)
main_game([0,0,0,0,0,0])
