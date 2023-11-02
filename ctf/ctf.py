""" Main file for the game.
"""
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

# ----- Initialisation ----- #

# -- Initialise the display
pygame.init()
pygame.display.set_mode()

# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0, 0.0)
space.damping = 0.1  # Adds friction to the ground for all objects

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
#   List of all game objects
game_objects_list = []
tanks_list = []

# -- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

# <INSERT GENERATE BACKGROUND>
background = pygame.Surface(screen.get_size())

for y in range(0,  current_map.height):
    for x in range(0,  current_map.width):
        background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))

# <INSERT CREATE BOXES>
#-- Create the boxes
for x in range(0, current_map.width):
    for y in range(0,  current_map.height):
        # Get the type of boxes
        box_type = current_map.boxAt(x, y)
        # If the box type is not 0 (aka grass tile), create a box
        if(box_type != 0):
            # Create a "Box" using the box_type, aswell as the x,y coordinates,
            # and the pymunk space
            box = gameobjects.get_box_with_type(x, y, box_type, space)
            game_objects_list.append(box)



# <INSERT CREATE TANKS>
#-- Create the tanks and the bases
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
    # Add the base for the tank to the game_objects_list
    game_objects_list.append(base)


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
            #print(tanks_list[0].body.position)
            if event.key == K_UP:
                tanks_list[0].accelerate()
            elif (event.key == K_DOWN):
                tanks_list[0].decelerate()
            elif (event.key == K_LEFT):
                tanks_list[0].turn_left()
            elif (event.key == K_RIGHT):
                tanks_list[0].turn_right()
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


        #   Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

    #   Control the game framerate
    clock.tick(FRAMERATE)
