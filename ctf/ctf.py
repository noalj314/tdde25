""" Main file for the game.
"""
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

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

    # -- Constants
FRAMERATE = 50

    # -- Variables
    #   Define the current level
current_map = maps.map0
screen = pygame.display.set_mode(current_map.rect().size)

    #   List of all game objects
game_objects_list = []
tanks_list = []
bullet_list = []


def remove_shape(space, shape, shape2=None):
    """Removes shapes and bodies from the space"""
    space.remove(shape, shape.body)
    if shape2:
        space.remove(shape2,shape2.body)
def remove_from_list(lst, obj):
    """Remove an object from its list"""
    lst.remove(obj)

def reset_tank(tank):
    "Reset the tanks posisiton to its starting posistion"
    tank.body.position = tank.start_position.x, tank.start_position.y
    tank.body.angle = tank.start_orientation

def collision_bullet_wood(arb, space, data):
    remove_shape(space,arb.shapes[0], arb.shapes[1])
    remove_from_list(bullet_list,arb.shapes[0].parent)
    remove_from_list(game_objects_list,arb.shapes[1].parent)
    return True

def collision_bullet_wall(arb, space, data):
    remove_shape(space, arb.shapes[0])
    remove_from_list(bullet_list, arb.shapes[0].parent)
    return True

def collision_bullet_tank(arb, space, data):
    remove_shape(space,arb.shapes[0], arb.shapes[0].body)
    remove_from_list(bullet_list, arb.shapes[0].parent)
    reset_tank(arb.shapes[1].parent)
    return True

def collision_handler(space, collision_type_x, collision_type_y, collision_bullet_z):
    handle = space.add_collision_handler(collision_type_x, collision_type_y)
    handle.pre_solve = collision_bullet_z
    return handle

b_w_handler = collision_handler(space,4,2,collision_bullet_wood)
b_s_handler = collision_handler(space, 4, 1, collision_bullet_wall)
b_m_handler = collision_handler(space, 4, 3, collision_bullet_wall)
b_m_handler = collision_handler(space, 4, 0, collision_bullet_wall)
#b_t_handler = collision_handler(space, 4, 5, collision_bullet_tank)


#Adds walls to prevent from going outside the screen
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
barrier(current_map,space)

# Generate background
def create_background(screen, current_map, images):
    """Creates a plain background with grass and no objects"""
    background = pygame.Surface(screen.get_size())
    for y in range(0,  current_map.height):
        for x in range(0,  current_map.width):
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))
    return background
background = create_background(screen, current_map, images)

#-- Create the boxes
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
            
create_boxes()

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
create_tanks()


# <INSERT CREATE FLAG>
#-- Create the flag

flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
game_objects_list.append(flag)

# ----- Main Loop -----#

# -- Control whether the game run
running = True

skip_update = 0
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
            elif (event.key == K_SPACE) and tanks_list[0].ability_to_shoot():
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
            game_objects_list.remove(tank.flag)
            flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
            game_objects_list.append(flag)
            
            tank.body.position = tank.start_position.x, tank.start_position.y
            tank.body.angle = tank.start_orientation
            tank.flag = None
            tank.score += 1
            for i in range(len(tanks_list)):
                print(f"Player {i+1}: {tanks_list[i].score}")


    #

    # -- Update Display

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
