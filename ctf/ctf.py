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
bullet_list = []

def collision_bullet_wood(arb, space, data):
    space.remove(arb.shapes[0], arb.shapes[0].body)
    space.remove(arb.shapes[1], arb.shapes[1].body)
    bullet_list.remove(arb.shapes[0].parent)
    game_objects_list.remove(arb.shapes[1].parent)
    return True

def collision_bullet_wall(arb, space, data):
    space.remove(arb.shapes[0], arb.shapes[0].body)
    bullet_list.remove(arb.shapes[0].parent)
    return True

def collision_bullet_tank(arb, space, data):
    space.remove(arb.shapes[0], arb.shapes[0].body)
    bullet_list.remove(arb.shapes[0].parent)
    arb.shapes[1].parent.body.position = arb.shapes[1].parent.start_position.x, arb.shapes[1].parent.start_position.y
    arb.shapes[1].parent.body.angle = arb.shapes[1].parent.start_orientation
    return True

b_w_handler = space.add_collision_handler(4, 2)
b_w_handler.pre_solve = collision_bullet_wood
b_s_handler = space.add_collision_handler(4, 1)
b_s_handler.pre_solve = collision_bullet_wall
b_m_handler = space.add_collision_handler(4, 3)
b_m_handler.pre_solve = collision_bullet_wall
b_m_handler = space.add_collision_handler(4, 0)
b_m_handler.pre_solve = collision_bullet_wall
b_t_handler = space.add_collision_handler(4, 5)
b_t_handler.pre_solve = collision_bullet_tank

# -- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

#Adds walls to prevent from going outside the screen
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
            box.shape.collision_type = box_type
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
    #Add collision_type for the tank
    tank.shape.collision_type = gameobjects.collision_types["tank"]
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
