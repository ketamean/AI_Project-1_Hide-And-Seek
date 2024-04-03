from problem import *
from obstacle import *
from player import *

class Level1:
    pass

class Node:
    def __init__(self, id_row: int, id_col: int, cumulative_pathcost: int, parent = None) -> None:
        # parent: parent node; is None if root node
        # coordinate: the state
        self.parent = parent
        self.coordinate = (id_row, id_col)
        self.h
        self.g = cumulative_pathcost
        self.f = self.h + self.g

class Level2:
    _all_announcements = []
    def __init__(self, input_filepath: str) -> None:
        """
            there are 3 kinds of map:
            - original map: problem.map_list
            - map of vision: viewable cells
            - map of heuristic: heuristics value only (-1, 0-999, 1000)
        """
        # a frame to build vision of a player
        # cells in the vision are numbered from 0 to (2r+1)^2 - 1
        # the following list contains multiple sublists, each of which is at index i and is a sequence of cell numbers that become unviewable when the cell i is a wall
        Level2.__vision_convention = None
        self.problem = Problem(
            input_filename=input_filepath,
            allow_move_obstacles=False
        )
        seeker = self.problem.seeker
        seeker.origin_map = self.problem.map_list
        
        skelaton_map = []
        for row in self.origin_map:
            tmp_row = []
            for cell in row:
                if cell == -1:
                    tmp_row.append(-1)
                else:
                    tmp_row.append(1000)
        from copy import deepcopy
        seeker.vision_map = deepcopy(skelaton_map)
        seeker.heuristic_map = deepcopy(skelaton_map)
        seeker.skelaton_map = skelaton_map

    def run(self, input_filepath: str):
        nhiders = len(self.problem.hiders)
        seeker = self.problem.seeker
        frontier = {
            seeker.coordinate: Node(
                id_row=seeker.coordinate[0],
                id_col=seeker.coordinate[1],
                cumulative_pathcost=0,
                parent=None
            )
        }
        reached = [seeker.coordinate]