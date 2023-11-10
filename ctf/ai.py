""" This file contains function and classes for the Artificial Intelligence used in the game.
"""

import math
from collections import defaultdict, deque

import pymunk
from pymunk import Vec2d
import gameobjects

# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(3)   # 3 degrees, a bit more than we can turn each tick


def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2):
    """ Compute the difference between two angles.
    """
    return (angle1 % (2 * math.pi)) - (angle2 % (2 * math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank, game_objects_list, tanks_list, space, currentmap):
        self.tank = tank
        self.game_objects_list = game_objects_list
        self.tanks_list = tanks_list
        self.space = space
        self.currentmap = currentmap
        self.flag = None
        self.max_x = currentmap.width - 1
        self.max_y = currentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def decide(self):
        """ Main decision function that gets called on every tick of the game.
        """
        
        distances = {}
        parents = {}
        self.lila(self.get_tile_of_position(self.tank.body.position), distances, parents)#path = self.find_shortest_path()
        #for i in path:
        #    print(i)
        return
        #pass  # To be implemented

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot.
        """
        pass  # To be implemented

    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """
        while True:
            yield

    def find_shortest_path(self):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """
        # To be implemented
        shortest_path = deque([])
        
        queue = deque([self.get_tile_of_position(self.tank.body.position)])
        visited = []
        parents = {}
        
        while queue:
            node = queue[0]
            queue.popleft()
            if node == self.get_target_tile():
                return node
            for i in self.get_tile_neighbors(self.get_tile_of_position(self.tank.body.position)):
                print(f"vistied {visited}")
                if not visited.__contains__(i):
                    visited.append(i)
                    parents[i] = node
                    queue.append(i)
                    print(parents)
        shortest_path.appendleft(self.get_target_tile())
        self.add_parent(parents, shortest_path)
        return deque(shortest_path)
        
    def lila(self, tile, distances, parents):
        for i in self.get_tile_neighbors(tile):
            print("as")
            try:
                if (i in distances and distances[i] > distances[tile] + 1) or not i in distances:
                    distances[i] = distances[tile] + 1
                    parents[i] = tile
                    print("aa")
                    if self.get_target_tile == i:
                        lista = [self.get_target_tile]
                        new_list = self.get_parent_list(self.get_target_tile, parents, lista)
                        return new_list
            except KeyError:
                print("asadasd")
                distances[i] = 1
            self.get_parent_list(self.get_target_tile, parents, [])
            self.lila(i, distances, parents)
    
    def get_parent_list(self, tile, parent_dict, output_list):
        output_list.append(parent_dict[tile])
        get_parent_list(parent_dict[tile], parent_dict, output_list)
        if parent_dict[tile] == self.get_tile_of_position(self.tank.body.position):
            print(output_list)
            return output_list
    
    def add_parent(self, parents, path):
        try:
            path.append(parents[path[-1]])
            add_parent(parents, path)
        except KeyError:
            return path
        return path


    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.get_flag()  # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
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
            or a wooden box.
        """
        neighbors = []  # Find the coordinates of the tiles' four neighbors
        neighbors.append(Vec2d(coord_vec[0],coord_vec[1]) + Vec2d(0,1))
        neighbors.append(Vec2d(coord_vec[0],coord_vec[1]) + Vec2d(1,0))
        neighbors.append(Vec2d(coord_vec[0],coord_vec[1]) + Vec2d(-1,0))
        neighbors.append(Vec2d(coord_vec[0],coord_vec[1]) + Vec2d(0,-1))
        return filter(self.filter_tile_neighbors, neighbors)

    def filter_tile_neighbors(self, coord):
        """ Used to filter the tile to check if it is a neighbor of the tank.
        """
        if 0 <= coord.x <= self.max_x and 0 <= coord.y <= self.max_y and self.currentmap.boxAt(coord.x, coord.y) == 0:
            return True
        return False