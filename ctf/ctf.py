import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import sys
import random
import math


# ----- Initialisation ----- #

# -- Initialise the display
pygame.init()
screen = pygame.display.set_mode((800, 600))
ui_screen = pygame.display.set_mode((800, 600))
UI_WIDTH = 200

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
import game_over

# -- Constants
multiplayer = None

# ----- Main Game -----#


def main_game(score=[]):
    """ The main game. """
    sounds.play_sound(sounds.engine_sound, 0.02)
    # -- Initialise the physics
    space = pymunk.Space()
    space.gravity = (0.0, 0.0)
    space.damping = 0.1  # Adds friction to the ground for all objects

    # -- Initialise global variables
    global multiplayer, current_map, screen, control_mode

    # -- List of all game objects
    current_map = menu.current_map
    multiplayer = menu.multiplayer
    screen = menu.screen
    game_objects_list = []
    tanks_list = []
    bullet_list = []
    ai_list = []
    powerups_list = {}  # The powerups on screen
    powerup_defines = [
        (images.mushroom, gameobjects.Modifier(15, 0.0, 0.0, 4, 1, 0.0, 0.0)),
        (images.star, gameobjects.Modifier(5, 1.0, 0.5, 10, 3, 0.0, 1.0)),
        (images.coin, gameobjects.Modifier(999, 0.0, 0.0, 0, 0, 0.0, 0.0)),
        (images.flower, gameobjects.Modifier(10, 0.0, 3.0, 0, 0, 0.0, 0.0)),
    ]

    def remove_shape(space, shape, shape2=None):
        """ Removes shapes and bodies from the space. """
        space.remove(shape, shape.body)
        if shape2:
            space.remove(shape2, shape2.body)

    def remove_from_list(lst, obj):
        """ Remove an object from its list. """
        lst.remove(obj)

    def reset_tank(tank):
        """ Reset the tanks position to its starting position. """
        tank.body.angle = tank.start_orientation
        tank.body.position = tank.start_position.x, tank.start_position.y
        tank.respawn = 0

    def drop_flag(tank, flag):
        """ Drops the flag at the tanks current position. """
        gameobjects.Flag(tank.body.position.x, tank.body.position.y)
        tank.flag = None
        flag.is_on_tank = False
        return flag

    def hit(item, bullet):
        """ Update the dictionary hit_points if a tank or wood wall is hit. """
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
        """
        Triggered when bullet and wooden box collide, removing both from the space and their lists.
        """
        bullet = arb.shapes[0].parent
        remove_shape(space, arb.shapes[0])
        sounds.play_sound(sounds.explosion_sound)
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit wood")
        return hit(arb.shapes[1].parent, bullet)

    def collision_bullet_wall(arb, space, data):
        """
        Triggered when bullet and wall collide, removing the bullet from the space and bullet_list. """
        remove_shape(space, arb.shapes[0])
        sounds.play_sound(sounds.explosion_sound)
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit wall")
        return True

    def collision_bullet_tank(arb, space, data):
        """
        Triggered when bullet and tank collide, removing the bullet from the space and bullet_list and resetting the position of the tank."""
        tank = arb.shapes[1].parent
        bullet = arb.shapes[0].parent
        remove_shape(space, arb.shapes[0])
        sounds.play_sound(sounds.explosion_sound)
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit wall")
        if gameobjects.Tank.ability_to_die(tank):
            return hit(tank, bullet)
        return True

    def collision_bullet_bullet(arb, space, data):
        """
        Triggered when bullet and another bullet collide, removing the bullets from the space and bullet_list.
        """
        remove_shape(space, arb.shapes[0], arb.shapes[1])
        sounds.play_sound(sounds.explosion_sound)
        try:
            remove_from_list(bullet_list, arb.shapes[0].parent)
            remove_from_list(bullet_list, arb.shapes[1].parent)
        except ValueError:
            print("Unable to remove bullet from bullet_list when hit other bullet")
        return True

    def collision_handler(space, object1, object2, collision_function):
        """
        Creates a CollisionHandler with two collision_types and a function which triggers on contact."""
        handle = space.add_collision_handler(object1, object2)
        handle.pre_solve = collision_function
        return handle

    # -- Handle all the different collisions
    b_w_handler = collision_handler(space, 4, 2, collision_bullet_wood)
    b_s_handler = collision_handler(space, 4, 1, collision_bullet_wall)
    b_m_handler = collision_handler(space, 4, 3, collision_bullet_wall)
    b_metal_handler = collision_handler(space, 4, 0, collision_bullet_wall)  # For hitting map border
    b_t_handler = collision_handler(space, 4, 5, collision_bullet_tank)
    b_b_handler = collision_handler(space, 4, 4, collision_bullet_bullet)

    def barrier(current_map, space):
        """ Adds a barrier to prevent from going outside the screen. """
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
        """ Creates a plain background with grass and no objects. """
        background = pygame.Surface(screen.get_size())
        for y in range(0, current_map.height):
            for x in range(0, current_map.width):
                background.blit(images.grass, (x * images.TILE_SIZE, y * images.TILE_SIZE))
        return background

    def create_boxes():
        """ Adds boxes to the map that acts as physical objects. """
        for x in range(0, current_map.width):
            for y in range(0, current_map.height):
                # Get the type of boxes
                box_type = current_map.boxAt(x, y)
                # If the box type is not 0 (aka grass tile), create a box
                if (box_type != 0):
                    # Create a "Box" using the box_type, aswell as the x,y coordinates, and the pymunk space
                    box = gameobjects.get_box_with_type(x, y, box_type, space)
                    box.shape.collision_type = box_type
                    game_objects_list.append(box)

    def create_tanks():
        """ Creates tanks for every start position of the map. """
        # Loop over the starting poistion
        for i in range(0, len(current_map.start_positions)):
            # Get the starting position of the tank "i"
            pos = current_map.start_positions[i]
            # Create the tank, images.tanks contains the image representing the tank
            tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
            # create the base at the same place as the tank
            base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])
            # Add the tank to the list of tanks
            tanks_list.append(tank)
            # Add collision_type for the tank
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
        """ Creates the flag in desired position. """
        flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
        game_objects_list.append(flag)
        return flag

    def update_ui():
        """ Updates the visual menu with different stats such as score, fire rate... """
        for i in range(len(tanks_list)):
            # Draw everyone's stats menu
            place = pygame.Rect((screen.get_size()[0] - UI_WIDTH) * (i % 2), screen.get_size()[1] / int(len(tanks_list) / 2) * (i // 2), UI_WIDTH, screen.get_size()[1] / int(len(tanks_list) / 2))
            colour = images.colours[i]

            pygame.draw.rect(screen, colour, place)

            # Draw HP/max HP as filled/empty boxes
            text_surface = my_font.render('HP:', False, (0, 0, 0))
            screen.blit(text_surface, (place.x + 10, place.y + 10))
            for j in range(tanks_list[i].max_hp):
                rect = pygame.Rect(place.x + (j + 4) * 11, place.y + 14, 10, 20)
                pygame.draw.rect(screen, 0x000000, rect)
            for j in range(tanks_list[i].hp):
                rect = pygame.Rect(place.x + (j + 4) * 11, place.y + 14, 10, 20)
                pygame.draw.rect(screen, 0x00ff00, rect)

            # Write all stats of the tank below HP
            menu.text_creator(screen, my_font, 'Score ' + str(tanks_list[i].score), 0x000000, (place.x + 10, place.y + 30))
            menu.text_creator(screen, my_font, 'Dmg ' + str(tanks_list[i].damage), 0x000000, (place.x + 10, place.y + 50))
            menu.text_creator(screen, my_font, 'Fire Rate ' + str(tanks_list[i].fire_rate) + "/s", 0x000000, (place.x + 10, place.y + 70))
            menu.text_creator(screen, my_font, 'Speed ' + str(tanks_list[i].max_speed), 0x000000, (place.x + 10, place.y + 90))
            menu.text_creator(screen, my_font, 'Bullet Speed ' + str(tanks_list[i].bullet_speed), 0x000000, (place.x + 10, place.y + 110))

            # Modifiers are shown as icons, and go like clock
            for j in range(len(tanks_list[i].modifiers.keys())):
                rect = pygame.Rect(place.x + j * images.TILE_SIZE, place.y + 130, images.TILE_SIZE, images.TILE_SIZE)
                menu.text_creator(screen, my_font, str(list(tanks_list[i].modifiers.keys())[j]), 0x000000, (rect.x + 10, rect.y + 10))
                pygame.draw.arc(screen, 0x000000, rect, 0, 2 * math.pi * (1 - list(tanks_list[i].modifiers.values())[j].time / list(tanks_list[i].modifiers.values())[j].orig.time), 8)

    def object_functions():
        """ Calls functions to initialise the objects. """

        barrier(current_map, space)
        create_boxes()
        create_tanks()

    object_functions()
    flag = create_flag()

    def event_handler(running):
        """ Handles all events. """
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
                    tanks_list[0].shoot(space, bullet_list)
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
                        tanks_list[1].shoot(space, bullet_list)
                if (event.type == KEYUP):
                    if event.key == K_w:
                        tanks_list[1].stop_moving()
                    elif (event.key == K_s):
                        tanks_list[1].stop_moving()
                    elif (event.key == K_a):
                        tanks_list[1].stop_turning()
                    elif (event.key == K_d):
                        tanks_list[1].stop_turning()
        return running

    def tank_won(tank):
        """ Checks if a tank has won the game. """
        sounds.win_sound.play()  # Play win sound
        game_objects_list.remove(tank.flag)
        flag = create_flag()
        tank.flag = None
        tank.score += 1
        for sound in sounds.sounds_list:
            sounds.stop_sound(sound)
        score_list = game_over.game_over(current_map, tanks_list, UI_WIDTH)
        main_game(score_list)

        pygame.display.flip()

    def update_objects():
        """ Updates the objects on the screen. """
        # Update object that depends on an other object position (for instance a flag)
        for obj in game_objects_list:
            obj.post_update()
        for obj in game_objects_list:
            obj.update_screen(screen, UI_WIDTH)
        for tank in tanks_list:
            tank.update_screen(screen, UI_WIDTH)
        for bullet in bullet_list:
            bullet.update_screen(screen, UI_WIDTH)
        for obj in powerups_list.values():
            obj.update_screen(screen, UI_WIDTH)

    def bots():
        """ Updates the ai. """
        for ai in ai_list:
            ai.decide()

    def powerup():
        """ Spawns powerups. """
        if random.randint(1, 100) > 98:
            x = random.randint(0, current_map.width - 1)
            y = random.randint(0, current_map.height - 1)

            if current_map.boxAt(x, y) == 0:
                powerup = gameobjects.PowerUp(x + 0.5, y + 0.5, powerup_defines[random.randint(0, len(powerup_defines) - 1)])
                powerups_list[(x + 0.5, y + 0.5)] = powerup

    def update_physics():
        """ Updates the physics of the game. """
        for obj in game_objects_list:
            obj.update()
        for obj in tanks_list:
            obj.update()
        for obj in bullet_list:
            obj.update()

    def update_tanks():
        """ Updates the tanks. """
        for tank in tanks_list:
            # Try to grab the flag and then if it has the flag update the posistion of the tank
            tank.try_grab_flag(flag)
            tank.try_grab_powerup(powerups_list)
            tank.post_update()
            for i in tank.modifiers.keys():
                tank.modifiers[i].tick()
            if tank.has_won():
                tank_won(tank)

    running = True
    skip_update = 0
    score_screen_background = pygame.Surface(screen.get_size())
    score_screen_background.fill(pygame.Color("black"))

    while running:
        # -- Main loop
        # -- Update physics
        if skip_update == 0:
            update_physics()
            skip_update = 2
        else:
            skip_update -= 1

        # -- Handle the events
        running = event_handler(running)

        # Check collisions and update the objects position
        space.step(1 / gameobjects.FRAMERATE)

        # Update the tanks
        update_tanks()

        background = create_background(screen, current_map, images)

        # Creates powerups
        powerup()

        # Update Display
        screen.blit(background, (UI_WIDTH, 0))

        # Call functions to update the display
        update_ui()

        # Update the display of the game objects on the screen
        update_objects()

        # Update ai
        bots()

        # Redisplay the entire screen (see double buffer technique)
        pygame.display.flip()

        # Control the game framerate
        clock.tick(gameobjects.FRAMERATE)


menu.welcome_screen(UI_WIDTH)

main_game([0, 0, 0, 0, 0, 0])
