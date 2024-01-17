import images
import pygame


class Map:
    """ An instance of Map is a blueprint for how the game map will look. """

    def __init__(self, width, height, boxes, start_positions, flag_position):
        """ Takes as argument the size of the map (width, height), an array with the boxes type,
        the start position of tanks (start_positions) and the position of the flag (flag_position).
        """
        self.width = width
        self.height = height
        self.boxes = boxes
        self.start_positions = start_positions
        self.flag_position = flag_position

    def rect(self):
        return pygame.Rect(0, 0, images.TILE_SIZE * self.width, images.TILE_SIZE * self.height)

    def boxAt(self, x, y):
        """ Return the type of the box at coordinates (x, y). """
        return self.boxes[y][x]

    def gen_thumbnail(self, thumb_size=(100, 100)):
        thumb = pygame.Surface(thumb_size)
        box_width = thumb_size[0] / self.width
        box_height = thumb_size[1] / self.height
        for y in range(self.height):
            for x in range(self.width):
                boxtype = self.boxAt(x, y)
                color = self.color_box(boxtype)
                pygame.draw.rect(thumb, color, (x * box_width, y * box_height, box_width, box_height))

        return thumb

    def color_box(self, boxtype):
        if boxtype == 0:
            return pygame.Color("green")
        elif boxtype == 1:
            return pygame.Color("grey")
        elif boxtype == 2:
            return pygame.Color("brown")
        elif boxtype == 3:
            return pygame.Color("white")


map0 = Map(9, 9,
           [[0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 2, 0, 2, 0, 1, 0],
            [0, 2, 0, 1, 0, 1, 0, 2, 0],
            [0, 0, 0, 1, 0, 1, 0, 0, 0],
            [1, 1, 0, 3, 0, 3, 0, 1, 1],
            [0, 0, 0, 1, 0, 1, 0, 0, 0],
            [0, 2, 0, 1, 0, 1, 0, 2, 0],
            [0, 1, 0, 2, 0, 2, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0]],
           [[0.5, 0.5, 0], [8.5, 0.5, 0], [0.5, 8.5, 180], [8.5, 8.5, 180]], [4.5, 4.5])

map1 = Map(15, 11,
           [[0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 1, 0, 3, 1, 1, 0, 0, 0, 1, 1, 3, 0, 1, 0],
            [0, 2, 0, 0, 3, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0],
            [2, 1, 0, 1, 1, 0, 1, 3, 1, 0, 1, 1, 0, 1, 2],
            [1, 1, 3, 0, 3, 2, 3, 0, 3, 2, 3, 0, 3, 1, 1],
            [2, 1, 0, 1, 1, 0, 1, 3, 1, 0, 1, 1, 0, 1, 2],
            [0, 2, 0, 0, 3, 0, 0, 2, 0, 0, 3, 0, 0, 2, 0],
            [0, 1, 0, 3, 1, 1, 0, 0, 0, 1, 1, 3, 0, 1, 0],
            [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
            [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0]],
           [[0.5, 0.5, 0], [14.5, 0.5, 0], [0.5, 10.5, 180], [14.5, 10.5, 180], [7.5, 0.5, 0], [7.5, 10.5, 180]], [7.5, 5.5])

map2 = Map(10, 5,
           [[0, 2, 0, 2, 0, 0, 2, 0, 2, 0],
            [0, 3, 0, 1, 3, 3, 1, 0, 3, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 3, 0, 1, 3, 3, 1, 0, 3, 0],
            [0, 2, 0, 2, 0, 0, 2, 0, 2, 0]],
           [[0.5, 2.5, 270], [9.5, 2.5, 90]], [5, 2.5])

map3 = Map(15, 15,
           [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
           [[0.5, 0.5, 0], [15, 0.5, 0], [0.5, 14.5, 180], [14.5, 14.5, 180]], [7.5, 7.5])

maps_list = ['map0', 'map1', 'map2', 'map3']
maps_list_no_str = [map0, map1, map2, map3]
