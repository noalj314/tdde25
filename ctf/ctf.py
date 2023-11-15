""" Main file for the game.
"""
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import sys

# ----- Initialisation ----- #

# -- Initialise the physics
space = pymunk.Space()
space.gravity = (0.0, 0.0)
space.damping = 0.1  # Adds friction to the ground for all objects

# -- Initialise the display
pygame.init()
pygame.display.set_mode()

# -- Initialise the clock
clock = pygame.time.Clock()



# -- Import from the ctf framework
# The framework needs to be imported after initialisation of pygame

import ai
import images
import gameobjects
import maps
import sounds

    # -- Constants
FRAMERATE = 50

    # -- Variables
    #   Define the current level
multiplayer = True if '--hot-multiplayer' in sys.argv else False
current_map = maps.map0
screen = pygame.display.set_mode(current_map.rect().size)

    # -- List of all game objects
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

def drop_flag(tank,flag):
    gameobjects.Flag(tank.body.position.x, tank.body.position.y)
    tank.flag = None
    flag.is_on_tank = False
    return flag


#def hit():

def collision_bullet_wood(arb, space, data):
    """Triggered when bullet and wooden box collide, removing both from the space and their lists."""
    remove_shape(space,arb.shapes[0], arb.shapes[1])
    sounds.explosion_sound.play()
    try:
        remove_from_list(bullet_list,arb.shapes[0].parent)
    except ValueError:
        print("Unable to remove bullet from bullet_list when hit wood")
    try:
        remove_from_list(game_objects_list,arb.shapes[1].parent)
    except ValueError:
        print("Unable to remove box from game_objects_list")
    return True

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
    remove_shape(space, arb.shapes[0])
    sounds.explosion_sound.play()
    if arb.shapes[1].parent.flag:
        drop_flag(arb.shapes[1].parent, flag)
    try:
        remove_from_list(bullet_list, arb.shapes[0].parent)
    except ValueError:
        print("Unable to remove bullet from bullet_list when hit wall")
    reset_tank(arb.shapes[1].parent)
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


# Adds walls to prevent from going outside the screen
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

# -- Generate background
def create_background(screen, current_map, images):
    """Creates a plain background with grass and no objects"""
    background = pygame.Surface(screen.get_size())
    for y in range(0,  current_map.height):
        for x in range(0,  current_map.width):
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))
    return background

# -- Create the boxes
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
            
# <INSERT CREATE TANKS>
#-- Create the tanks and the bases
def create_tanks():
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
        if multiplayer and i > 1:
            bot = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
            ai_list.append(bot)
        elif not multiplayer and i > 0:
            bot = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
            ai_list.append(bot)


# <INSERT CREATE FLAG>
#-- Create the flag
def create_flag():
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)
    return flag

flag = create_flag()
barrier(current_map,space)
background = create_background(screen, current_map, images)
create_boxes()
create_tanks()
# ----- Main Loop -----#

# -- Control whether the game run
running = True

skip_update = 0
skip_update_2 = 0
variabel = 0

while running:
    # -- Handle the events
    for event in pygame.event.get():
        # Check if we receive a QUIT event (for instance, if the user press the
        # close button of the wiendow) or if the user press the escape key.
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
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
                bullet_list.append(tanks_list[0].shoot(space))
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
                    bullet_list.append(tanks_list[1].shoot(space))
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
        # Loop over all the game objects and update their speed in function of their
        # acceleration.
        for obj in game_objects_list:
            obj.update()
        for obj in tanks_list:
            obj.update()
        for obj in bullet_list:
            obj.update()
        skip_update = 2
    else:
        skip_update -= 1

    #   Check collisions and update the objects position
    space.step(1 / FRAMERATE)

    #   Update object that depends on an other object position (for instance a flag)
    for obj in game_objects_list:
        obj.post_update()
    # Try to grab the flag and then if it has the flag update the posistion of the tank
    for tank in tanks_list:
        tank.try_grab_flag(flag)
        tank.post_update()
        
        if tank.has_won():
            sounds.win_sound.play() # play win sound
            game_objects_list.remove(tank.flag)
            flag = create_flag()
            
            tank.body.position = tank.start_position.x, tank.start_position.y
            tank.body.angle = tank.start_orientation
            tank.flag = None
            tank.score += 1
            for i in range(len(tanks_list)):
                print(f"Player {i+1}: {tanks_list[i].score}")
            for i in range(0, len(current_map.start_positions)):
                if not multiplayer and i > 0:
                    ai_list[i-1] = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)
                elif multiplayer and i > 1:
                    ai_list[i-2] = ai.Ai(tanks_list[i], game_objects_list, tanks_list, space, current_map)


    # Update ai
    def bots():
        for ai in ai_list:
            #ai = ai_list[2]
            #ai.update_grid_pos()
            ai.decide()
            #try:
                #ai.tank.body.position = ai.path[1].x + 0.5, ai.path[1].y + 0.5
            #except IndexError:
                #""
                #print(ai, "says ???")
            
            #print(ai.tank.body.position, ai.path)

    # -- Update Display
    bots()

    # <INSERT DISPLAY BACKGROUND>
    screen.blit(background, (0, 0))


    # <INSERT DISPLAY OBJECTS>
    # Update the display of the game objects on the screen
    for obj in game_objects_list:
        obj.update_screen(screen)
    for tank in tanks_list:
        tank.update_screen(screen)
    for bullet in bullet_list:
        bullet.update_screen(screen)


    #   Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

    #   Control the game framerate
    clock.tick(FRAMERATE)
