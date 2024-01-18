""" This file contains function and classes for the Artificial Intelligence used in the game.
"""

import math
from collections import deque

import images
import pymunk
from pymunk import Vec2d
import gameobjects


MIN_ANGLE_DIF = math.radians(3)   # 3 degrees, a bit more than we can turn each tick
MIN_XY_DIF = 0.05


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
    convert the resulting vector to get the correct angle for our space."""
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """ Compute the difference between two angles."""
    return (angle1 % (2 * math.pi)) - (angle2 % (2 * math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank, game_objects_list, tanks_list, bullet_list, space, currentmap):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.bullet_list = bullet_list
        self.space = space
        self.currentmap = currentmap
        self.flag = None
        self.max_x = currentmap.width - 1
        self.max_y = currentmap.height - 1
        self.move_cycle = self.move_cycle_gen()
        self.metal_boxes = False

        # Makes the ai-controlled tanks have a bonus to their movement and bullet speed
        self.tank.modifiers["ai"] = gameobjects.Modifier(999, 1.0, 0.0, 0, 0, 0.8, 0.0)

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position((self.tank.body.position.x, self.tank.body.position.y))

    def move_cycle_gen(self):
        """ Generator for a move cycle to move toward the next tile. """
        while True:
            every2 = 0  # To counteract delay in movement
            self.update_grid_pos()
            self.path = self.find_shortest_path(self.grid_pos, self.get_target_tile())

            if not self.path:  # If tank does not find path to flag
                self.metal_boxes = True  # then it will check paths containing metal boxes
                yield
                continue  # Start from the top of our cycle

            self.metal_boxes = False
            next_coord = self.path.popleft()
            last_distance = 10  # High value
            yield

            target_angle = angle_between_vectors(self.tank.body.position, next_coord + Vec2d(0.5, 0.5))
            dif_angle = periodic_difference_of_angles(self.tank.body.angle, target_angle)

            # Tank turns in most effective angle
            if dif_angle < -math.pi or 0 < dif_angle < math.pi:
                self.tank.turn_left()
                yield
            else:
                self.tank.turn_right()
                yield

            # When find right angle
            while abs(dif_angle) >= MIN_ANGLE_DIF:
                dif_angle = periodic_difference_of_angles(self.tank.body.angle, target_angle)
                yield

            self.tank.stop_turning()
            self.tank.accelerate()
            distance = self.tank.body.position.get_distance(next_coord + Vec2d(0.5, 0.5))
            while distance > 0.25 and last_distance >= distance:
                if every2 == 0:
                    last_distance = self.tank.body.position.get_distance(next_coord + Vec2d(0.5, 0.5))
                    every2 = 1
                else:
                    every2 -= 1
                distance = self.tank.body.position.get_distance(next_coord + Vec2d(0.5, 0.5))
                yield
            self.tank.stop_moving()
            yield

    def decide(self):
        """ Called every tick, tank shoots and moves. """
        self.maybe_shoot()
        next(self.move_cycle)

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
        or a wooden box is found, then we shoot."""
        angle = self.tank.body.angle + math.pi / 2

        x_start = self.tank.body.position.x + (0.4 * math.cos(angle))
        y_start = self.tank.body.position.y + (0.4 * math.sin(angle))

        x_end = self.tank.body.position.x + (max(self.max_x, self.max_y) * math.cos(angle))
        y_end = self.tank.body.position.y + (max(self.max_x, self.max_y) * math.sin(angle))

        res = self.space.segment_query_first((x_start, y_start), (x_end, y_end), 0.3, pymunk.ShapeFilter())
        try:
            # Shoots if sees another tank or a wooden box
            if isinstance(res, pymunk.SegmentQueryInfo) and hasattr(res.shape, 'parent'):
                if (isinstance(res.shape.parent, gameobjects.Tank) or (isinstance(res.shape.parent, gameobjects.Box) and res.shape.parent.sprite == images.woodbox)) and res.shape.parent != self.tank:
                    self.tank.shoot(self.space, self.bullet_list)
        except AttributeError:
            print("Error")

    def find_shortest_path(self, start, end):
        """ A simple Breadth First Search using integer coordinates as our nodes.
        Edges are calculated as we go, using an external function."""
        queue = deque([(start, deque([start]))])  # Each element: (current_position, path)
        visited = set()
        while queue:
            (node, path) = queue.popleft()
            if node == end:
                path.popleft()
                if end == Vec2d(int(self.flag.x), int(self.flag.y)):
                    path.append(Vec2d(self.flag.x - 0.5, self.flag.y - 0.5))
                elif end == Vec2d(int(self.tank.start_position.x), int(self.tank.start_position.y)):
                    path.append(Vec2d(self.tank.start_position.x - 0.5, self.tank.start_position.y - 0.5))
                return path
            if node in visited:
                continue
            visited.add(node)

            # Adds the path to all neighbouring tiles
            for neighbour in self.get_tile_neighbors(node):
                new_pos = Vec2d(neighbour.x, neighbour.y)
                queue.append((new_pos, path + deque([new_pos])))
        return deque()  # No valid path found

    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
        return the position of our home base."""
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.get_flag()  # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
        where it is when the Ai object is initialized. """
        if self.flag is None:
            # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec):
        """ Returns all bordering grid squares of the input coordinate.
        A bordering square is only considered accessible if it is grass
        or a wooden box. """
        neighbors = []  # Find the coordinates of the tiles' four neighbors
        neighbors.append(Vec2d(coord_vec[0], coord_vec[1]) + Vec2d(0, 1))
        neighbors.append(Vec2d(coord_vec[0], coord_vec[1]) + Vec2d(1, 0))
        neighbors.append(Vec2d(coord_vec[0], coord_vec[1]) + Vec2d(-1, 0))
        neighbors.append(Vec2d(coord_vec[0], coord_vec[1]) + Vec2d(0, -1))
        return filter(self.filter_tile_neighbors, neighbors)

    def filter_tile_neighbors(self, coord):
        """ Used to filter the tile to check if it is a neighbor of the tank. """
        if 0 <= coord.x <= self.max_x and 0 <= coord.y <= self.max_y and (self.currentmap.boxAt(coord.x, coord.y) == 0 or self.currentmap.boxAt(coord.x, coord.y) == 2 or (self.currentmap.boxAt(coord.x, coord.y) == 3 and self.metal_boxes)):
            return True
        return False
