from problem import *
from obstacle import *
from player import *
from pq import *
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
    _all_announcements = []     # to keep all announcements
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
        for row in self.problem.map_list:
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
    
    @staticmethod
    def setup_heuristic_map(seeker: Seeker):
        """
            set up heuristic map of the seeker (seeker.heuristic_map)

            returns nothing
        """
        from copy import deepcopy
        seeker.heuristic_map = deepcopy(seeker.skelaton_map)
        seeker.vision()
        pos_r, pos_c = seeker.coordinate
        mark_hider = []         # mark all hiders in the vision
        mark_announcement = []  # mark all announcements in the vision

        # traverse seeker.vision_map
        for idrow in range(-seeker.radius, seeker.radius + 1, +1):
            # idrow in [-radius, radius + 1)
            if idrow < 0:
                continue
            if idrow >= len(seeker.vision_map):
                break
            for idcol in range(-seeker.radius, seeker.radius + 1, +1):
                # idcol in [-radius, radius + 1)
                if idcol < 0:
                    continue
                if idcol >= len(seeker.vision_map[0]):
                    break
                if seeker.vision_map[idrow][idcol] == True:
                    cell = seeker.origin_map[idrow][idcol]
                    if -1 in cell:
                        # is wall
                        if len(cell) > 1:
                            # exists announcement(s) on this wall
                            seeker.heuristic_map[idrow][idcol] = 0
                        else:
                            seeker.heuristic_map[idrow][idcol] = 1000
                    elif 1000 in cell:
                        # empty cell
                        if cell != [1000]:
                            # invalid map!
                            raise ValueError("An empty cell cannot contain any objects")
                        seeker.heuristic_map[idrow][idcol] = 1000
                    else:
                        # list has only Hider - Seeker - Announcement object
                        for component in cell:
                            # have not done
                            
                # else, heuristic value of the corresponding cell remains unchanged

    def run(self):
        nhiders = len(self.problem.hiders)
        seeker = self.problem.seeker
        reached = {
            seeker.coordinate: Node(
                id_row=seeker.coordinate[0],
                id_col=seeker.coordinate[1],
                cumulative_pathcost=0,
                parent=None
            )
        }
        
        frontier = PriorityQueue( () )

        while len(frontier) > 0:
            pass

lv2 = Level2('test/map1_1.txt')
lv2.run()