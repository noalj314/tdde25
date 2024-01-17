""" This module contains support for the different game objects: tank, boxes...
"""
import math
import pygame
import pymunk
import sounds
import images
import copy
from pygame.examples.scaletest import SpeedTest
from urllib.request import HTTPPasswordMgr


FRAMERATE = 50
DEBUG = False  # Change this to set it in debug mode

collision_types = {
    "wall": 1,      # Walls stop tanks and destroy bullets
    "wood": 2,      # Wooden boxes are destroyed upon being shot
    "metal": 3,     # Metal boxes are pushed
    "bullet": 4,    # Bullets are destroyed upon hitting something
    "tank": 5,      # Tanks are destroyed when hit by bullets
}


def physics_to_display(x):
    """ This function is used to convert coordinates in the physic engine into the display coordinates """
    return x * images.TILE_SIZE


class GameObject:
    """ Mostly handles visual aspects (pygame) of an object.
        Subclasses need to implement two functions:
        - screen_position    that will return the position of the object on the screen
        - screen_orientation that will return how much the object is rotated on the screen (in degrees). """

    def __init__(self, sprite):
        self.sprite = sprite

    def update(self):
        """ Placeholder, supposed to be implemented in a subclass.
            Should update the current state (after a tick) of the object."""
        return

    def post_update(self):
        """ Should be implemented in a subclass. Make updates that depend on
            other objects than itself."""
        return

    def update_screen(self, screen, ui_width):
        """ Updates the visual part of the game. Should NOT need to be changed
            by a subclass."""
        sprite = self.sprite

        p = self.screen_position()  # Get the position of the object (pygame coordinates)
        sprite = pygame.transform.rotate(sprite, self.screen_orientation())  # Rotate the sprite using the rotation of the object

        # The position of the screen correspond to the center of the object,
        # but the function screen.blit expect to receive the top left corner
        # as argument, so we need to adjust the position p with an offset
        # which is the vector between the center of the sprite and the top left
        # corner of the sprite
        offset = pymunk.Vec2d(*sprite.get_size()) / 2.
        p = p - offset
        screen.blit(sprite, p + pymunk.Vec2d(ui_width, 0))  # Copy the sprite on the screen


class GamePhysicsObject(GameObject):
    """ This class extends GameObject and it is used for objects which have a
        physical shape (such as tanks and boxes). This class handle the physical
        interaction of the objects.
    """

    def __init__(self, x, y, orientation, sprite, space, movable):
        """ Takes as parameters the starting coordinate (x,y), the orientation, the sprite (aka the image
            representing the object), the physic engine object (space) and whether the object can be
            moved (movable).
        """

        super().__init__(sprite)

        # Half dimensions of the object converted from screen coordinates to physic coordinates
        half_width = 0.5 * self.sprite.get_width() / images.TILE_SIZE
        half_height = 0.5 * self.sprite.get_height() / images.TILE_SIZE

        # Physical objects have a rectangular shape, the points correspond to the corners of that shape.
        points = [[-half_width, -half_height],
                  [-half_width, half_height],
                  [half_width, half_height],
                  [half_width, -half_height]]
        self.points = points
        # Create a body (which is the physical representation of this game object in the physic engine)
        if movable:
            # Create a movable object with some mass and moments
            # (considering the game is a top view game, with no gravity,
            # the mass is set to the same value for all objects)."""
            mass = 10
            moment = pymunk.moment_for_poly(mass, points)
            self.body = pymunk.Body(mass, moment)
        else:
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)  # Create a non movable (static) object

        self.body.position = x, y
        self.body.angle = math.radians(orientation)       # orientation is provided in degress, but pymunk expects radians.
        self.start_orientation = math.radians(orientation)
        self.shape = pymunk.Poly(self.body, points)  # Create a polygon shape using the corner of the rectangle
        self.shape.parent = self

        # Add the object to the physic engine
        space.add(self.body, self.shape)

    def screen_position(self):
        """ Converts the body's position in the physics engine to screen coordinates. """
        return physics_to_display(self.body.position)

    def screen_orientation(self):
        """ Angles are reversed from the engine to the display. """
        return -math.degrees(self.body.angle)

    def update_screen(self, screen, ui_width):
        super().update_screen(screen, ui_width)
        # debug draw
        if DEBUG:
            ps = [self.body.position + p for p in self.points]

            ps = [physics_to_display(p) for p in ps]
            ps += [ps[0]]
            pygame.draw.lines(screen, pygame.color.THECOLORS["red"], False, ps, 1)


def clamp(min_max, value):
    """ Convenient helper function to bound a value to a specific interval. """
    return min(max(-min_max, value), min_max)


class Tank(GamePhysicsObject):
    """ Extends GamePhysicsObject and handles aspects which are specific to our tanks. """
    # Constant values for the tank, acessed like: Tank.ACCELERATION
    # You can add more constants here if needed later
    ACCELERATION = 0.4
    NORMAL_MAX_SPEED = 2.0
    FLAG_MAX_SPEED = NORMAL_MAX_SPEED * 0.5
    FIRE_RATE = 2
    HIT_POINTS = 4
    WEAPON_DAMAGE = 1
    BULLET_SPEED = 5
    ROTATION_SPEED = 3

    def __init__(self, x, y, orientation, sprite, space):
        super().__init__(x, y, orientation, sprite, space, True)
        # Define variable used to apply motion to the tanks
        self.acceleration = 0  # 1 forward, 0 for stand still, -1 for backwards
        self.rotation = 0  # 1 clockwise, 0 for no rotation, -1 counter clockwise
        self.shoot_last = 50  # set last shoot to 50 since the tank has not shoot
        self.respawn = 0  # respawn protection
        self.flag = None  # This variable is used to access the flag object, if the current tank is carrying the flag
        self.max_speed = Tank.NORMAL_MAX_SPEED  # Impose a maximum speed to the tank
        self.start_position = pymunk.Vec2d(x, y)  # Define the start position, which is also the position where the tank has to return with the flag
        self.score = 0
        self.fire_rate = Tank.FIRE_RATE
        self.hp = Tank.HIT_POINTS
        self.max_hp = Tank.HIT_POINTS
        self.speed_mod = 1
        self.damage = Tank.WEAPON_DAMAGE
        self.bullet_speed = Tank.BULLET_SPEED
        self.rotation_speed = Tank.ROTATION_SPEED
        self.modifiers = {}

    def accelerate(self, accelerate_mod=1):
        """ Call this function to make the tank move forward. """
        sounds.play_sound(sounds.movement_sound)  # Play the sound of the tank moving
        self.acceleration = 2 * accelerate_mod

    def stop_moving(self):
        """ Call this function to make the tank stop moving. """
        sounds.stop_sound(sounds.movement_sound)
        self.acceleration = 0
        self.body.velocity = pymunk.Vec2d.zero()

    def decelerate(self, decelerate_mod=1):
        """ Call this function to make the tank move backward. """
        sounds.play_sound(sounds.movement_sound)  # Play the sound of the tank moving
        self.acceleration = -2 * decelerate_mod

    def turn_left(self):
        """ Makes the tank turn left (counter clock-wise). """
        self.rotation = -self.rotation_speed

    def turn_right(self):
        """ Makes the tank turn right (clock-wise). """
        self.rotation = self.rotation_speed

    def stop_turning(self):
        """ Call this function to make the tank stop turning. """
        self.rotation = 0
        self.body.angular_velocity = 0

    def ability_to_shoot(self):
        """ Call this function to check whether a tank can shoot or not """
        return self.shoot_last >= FRAMERATE / self.fire_rate

    def ability_to_die(self):
        """ Call this function to check whether a tank can die or not """
        return self.respawn >= 100  # two seconds

    def update(self):
        """ A function to update the objects coordinates. Gets called at every tick of the game. """
        spd = 1  # Mult
        dmg = 0  # Add
        bspd = 1  # Mult
        rspd = 1  # Mult
        hp = 0  # Add
        fr = 1  # Mult
        damage_taken = self.max_hp - self.hp
        for i in self.modifiers.keys():
            if self.modifiers[i].time <= 0:
                del self.modifiers[i]
                break
            spd += self.modifiers[i].max_speed
            dmg += self.modifiers[i].damage
            bspd += self.modifiers[i].bullet_speed
            rspd += self.modifiers[i].rotation_speed
            hp += self.modifiers[i].max_hp
            fr += self.modifiers[i].fire_rate

        self.max_speed = Tank.NORMAL_MAX_SPEED * spd
        self.damage = Tank.WEAPON_DAMAGE + dmg
        self.bullet_speed = Tank.BULLET_SPEED * bspd
        self.rotation_speed = Tank.ROTATION_SPEED * rspd
        self.max_hp = Tank.HIT_POINTS + hp
        self.fire_rate = Tank.FIRE_RATE * fr
        self.hp = self.max_hp - damage_taken

        # Creates a vector in the direction we want accelerate / decelerate
        acceleration_vector = pymunk.Vec2d(0, self.ACCELERATION * self.acceleration).rotated(self.body.angle)
        # Applies the vector to our velocity
        self.body.velocity += acceleration_vector

        # Makes sure that we don't exceed our speed limit
        velocity = clamp(self.max_speed, self.body.velocity.length)
        self.body.velocity = pymunk.Vec2d(velocity, 0).rotated(self.body.velocity.angle)

        # Updates the rotation
        self.body.angular_velocity += self.rotation * self.ACCELERATION
        self.body.angular_velocity = clamp(self.max_speed, self.body.angular_velocity)
        self.respawn += 1
        self.shoot_last += 1

    def post_update(self):
        """ If the tank carries the flag, then update the positon of the flag """
        if (self.flag is not None):
            self.flag.x = self.body.position[0]
            self.flag.y = self.body.position[1]
            self.flag.orientation = -math.degrees(self.body.angle)
        # Else ensure that the tank has its normal max speed
        else:
            self.max_speed = Tank.NORMAL_MAX_SPEED * self.speed_mod

    def try_grab_flag(self, flag):
        """ Call this function to try to grab the flag, if the flag is not on other tank
            and it is close to the current tank, then the current tank will grab the flag."""
        # Check that the flag is not on other tank
        if not flag.is_on_tank:
            # Check if the tank is close to the flag
            flag_pos = pymunk.Vec2d(flag.x, flag.y)
            if (flag_pos - self.body.position).length < 0.5:
                # Grab the flag !
                self.flag = flag
                flag.is_on_tank = True
                self.max_speed = Tank.FLAG_MAX_SPEED * self.speed_mod
                sounds.play_sound(sounds.flag_capture_sound)  # Play the sound of the flag being captured

    def try_grab_powerup(self, powerups):
        """ Call this function to try to grab the flag, if the flag is not on other tank
            and it is close to the current tank, then the current tank will grab the flag.
        """
        try:
            powerup = powerups[(int(self.body.position[0]) + 0.5, int(self.body.position[1]) + 0.5)]
            self.modifiers[powerup.sprite] = copy.deepcopy(powerup.modifier)
            self.modifiers[powerup.sprite].orig = powerup.modifier
            del powerups[(int(self.body.position[0]) + 0.5, int(self.body.position[1]) + 0.5)]
            sounds.play_sound(sounds.flag_capture_sound)  # Play the sound of the flag being captured
        except KeyError:
            pass

    def has_won(self):
        """ Check if the current tank has won (if it is has the flag and it is close to its start position). """
        return self.flag is not None and (self.start_position - self.body.position).length < 0.2

    def shoot(self, space, bullet_list):
        """ Call this function to shoot a missile from the tank."""
        if Tank.ability_to_shoot(self):
            self.shoot_last = 0
            sounds.play_sound(sounds.tankshot_sound)  # Play the sound of the tank shooting
            bullet = Bullet(self, images.bullet, space)
            bullet.shape.collision_type = collision_types["bullet"]
            bullet_list.append(bullet)
        else:
            return None


class Bullet(GamePhysicsObject):
    """ Extends GamePhysicsObject and handles aspects which are specific to our tanks. """
    # You can add more constants here if needed later

    def __init__(self, tank, sprite, space):

        x_start = tank.body.position.x + (0.4 * math.cos(math.radians(tank.screen_orientation() - 90)))
        y_start = tank.body.position.y + (0.4 * math.sin(math.radians(tank.screen_orientation() + 90)))

        super().__init__(x_start, y_start, tank.screen_orientation(), sprite, space, True)
        # Define variable used to apply motion to the bullet
        self.speed = 5
        self.body.velocity = pymunk.Vec2d((self.speed * math.cos(math.radians(tank.screen_orientation() - 90))), self.speed * (math.sin(math.radians(tank.screen_orientation() + 90))))
        self.space = space
        self.max_speed = tank.bullet_speed    # Impose a maximum speed to the bullet
        self.damage = tank.damage

    def update(self):
        """ A function to update the objects coordinates. Gets called at every tick of the game. """
        # Applies the vector to our velocity
        damping_spacefctr = 1.0 / (1.0 - self.space.damping)
        self.body.velocity += (damping_spacefctr * self.body.velocity)

        # Makes sure that we dont exceed our speed limit
        velocity = clamp(self.max_speed, self.body.velocity.length)
        self.body.velocity = pymunk.Vec2d(velocity, 0).rotated(self.body.velocity.angle)


class Box(GamePhysicsObject):
    """ This class extends the GamePhysicsObject to handle box objects. """
    HIT_POINTS = 2

    def __init__(self, x, y, sprite, movable, space, destructable):
        """ It takes as arguments the coordinate of the starting position of the box (x,y) and the box model (boxmodel). """
        super().__init__(x, y, 0, sprite, space, movable)
        self.hp = Box.HIT_POINTS
        self.destructable = destructable


def get_box_with_type(x, y, type, space):
    """ Create a box with the correct type at coordinate x, y.
        - type == 1 create a rock box
        - type == 2 create a wood box
        - type == 3 create a metal box
        Other values of type are invalid
    """
    (x, y) = (x + 0.5, y + 0.5)  # Offsets the coordinate to the center of the tile
    if type == 1:  # Creates a non-movable non-destructable rockbox
        return Box(x, y, images.rockbox, False, space, False)
    if type == 2:  # Creates a movable destructable woodbox
        return Box(x, y, images.woodbox, True, space, True)
    if type == 3:  # Creates a movable non-destructable metalbox
        return Box(x, y, images.metalbox, True, space, False)


class GameVisibleObject(GameObject):
    """ This class extends GameObject for object that are visible on screen but have no physical representation (bases and flag) """

    def __init__(self, x, y, sprite):
        """ It takes argument the coordinates (x,y) and the sprite. """
        self.x = x
        self.y = y
        self.orientation = 0
        super().__init__(sprite)

    def screen_position(self):
        """ Overwrite from GameObject """
        return physics_to_display(pymunk.Vec2d(self.x, self.y))

    def screen_orientation(self):
        """ Overwrite from GameObject """
        return self.orientation


class PowerUp(GameVisibleObject):
    """ This class extends GameVisibleObject for representing powerups."""

    def __init__(self, x, y, defines):
        self.modifier = defines[1]
        super().__init__(x, y, defines[0])


class Flag(GameVisibleObject):
    """ This class extends GameVisibleObject for representing flags."""

    def __init__(self, x, y):
        self.is_on_tank = False
        super().__init__(x, y, images.flag)


class Modifier():
    def __init__(self, time, speed, firerate, maxhp, dmg, bulletspd, rotationspd):
        self.time = time
        self.max_hp = maxhp
        self.fire_rate = firerate
        self.max_speed = speed
        self.damage = dmg
        self.bullet_speed = bulletspd
        self.rotation_speed = rotationspd
        self.orig = self  # To refer to the base modifier's time

    def tick(self):
        self.time -= 1 / FRAMERATE
        self.time -= 1 / FRAMERATE
