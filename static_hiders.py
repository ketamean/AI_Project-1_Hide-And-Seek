from problem import *
from obstacle import *
from player import *
from pq import *
class Level1:
    announcement = []
    def __init__(self, input_filepath:str) -> None:
        self.problem = Problem(
            input_filename=input_filepath,
            allow_move_obstacles=False
        )
        seeker = self.problem.seeker
        hider = self.problem.hiders
        seeker.origin_map = self.problem.map_list

        skelaton_map = []
        for row in self.problem.map_list:
            row_skelation = []
            for cell in row:
                if -1 in cell:
                    row_skelation.append(-1)
                else:
                    row_skelation.append(1000)
            skelaton_map.append(row_skelation)

        from copy import deepcopy
        seeker.vision_map = deepcopy(skelaton_map)
        seeker.heuristic_map = deepcopy(skelaton_map)
        self.visited_map = deepcopy(skelaton_map)
        self.seen_map = deepcopy(skelaton_map)
        seeker.skelaton_map = skelaton_map
        seeker.vision()
        self.dict_vision = {}

        idrow = 0
        for row in seeker.vision_map:
            idcol = 0
            for cell in row:
                if cell == True:
                    self.seen_map[idrow][idcol] = True
                else:
                    self.seen_map[idrow][idcol] = False

                self.visited_map[idrow][idcol] = False
                idcol += 1
            idrow += 1
        
        r, c = seeker.coordinate
        self.visited_map[r][c] = True

        # for row in seen_map:
        #     for cell in row:
        #         # if cell == -1:
        #         #     print('x', end=' ')
        #         # elif cell == 1000:
        #         #     print('-', end=' ')
        #         if cell == True:
        #             print(1, end=' ')
        #         elif cell == False:
        #             print(0, end=' ')
        #     print()
        

    def set_up_heuristic_map(seeker: Seeker):
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
                            pass
                # else, heuristic value of the corresponding cell remains unchanged
    
    def update_seen_map(self, seeker: Seeker):
        """
            update the seen map of the seeker
        """
        idrow, idcol = seeker.coordinate
        for i in range(idrow - seeker.radius , idrow + seeker.radius):
            for j in range(idcol - seeker.radius, idcol + seeker.radius):
                if i < 0 or i >= len(seeker.seen_map) or j < 0 or j >= len(seeker.seen_map[0]):
                    continue
                seeker.seen_map[i][j] = True

    def update_vision_map(self, seeker: Seeker):
        """
            update the vision map of the seeker
            add the new vision to the dictionary
        """
        r, c = seeker.coordinate
        if (r,c) not in self.dict_vision:
            self.dict_vision[r,c] = seeker.vision_map

    def calculate_heuristic_method1(seeker : Seeker):
        """
        this function calculate the heuristic value by the NUMBER OF UNSEEN CELL
        """
        unseen_cell = 0

    def move_seeker(self, seeker: Seeker, action: str):
        idrow, idcol = seeker.coordinate
        if action == 'U':
            if idrow > 0 & seeker.skelaton_map[idrow - 1][idcol] != -1 & self.visited_map[idrow - 1][idcol] == False:
                # check if the cell is the previous state or not
                prev_row, prev_col = seeker.latest_states[len(seeker.latest_states) - 1]
                if prev_row != idrow - 1 or prev_col != idcol:
                    seeker.latest_states.append((idrow, idcol))
                    seeker.coordinate = (idrow - 1, idcol)
                    self.visited_map[idrow - 1][idcol] = True

    
    def run(self, seeker: Seeker, hiders: list[Hider]):
        announcement = []
        hider = hiders[0]
        while (seeker.coordinate != hider.coordinate):
            




class Node:
    def __init__(self, id_row: int, id_col: int, cumulative_pathcost: int, parent = None) -> None:
        # parent: parent node; is None if root node
        # coordinate: the state
        self.parent = parent
        self.coordinate = (id_row, id_col)
        self.h
        self.g = cumulative_pathcost
        self.f = self.h + self.g

# class Level2:
#     _all_announcements = []     # to keep all announcements
#     def __init__(self, input_filepath: str) -> None:
#         """
#             there are 3 kinds of map:
#             - original map: problem.map_list
#             - map of vision: viewable cells
#             - map of heuristic: heuristics value only (-1, 0-999, 1000)
#         """
#         # a frame to build vision of a player
#         # cells in the vision are numbered from 0 to (2r+1)^2 - 1
#         # the following list contains multiple sublists, each of which is at index i and is a sequence of cell numbers that become unviewable when the cell i is a wall
#         Level2.__vision_convention = None
#         self.problem = Problem(
#             input_filename=input_filepath,
#             allow_move_obstacles=False
#         )
#         seeker = self.problem.seeker
#         seeker.origin_map = self.problem.map_list
        
#         skelaton_map = []
#         for row in self.problem.map_list:
#             tmp_row = []
#             for cell in row:
#                 if cell == -1:
#                     tmp_row.append(-1)
#                 else:
#                     tmp_row.append(1000)
#         from copy import deepcopy
#         seeker.vision_map = deepcopy(skelaton_map)
#         seeker.heuristic_map = deepcopy(skelaton_map)
#         seeker.skelaton_map = skelaton_map
    
#     @staticmethod
#     def setup_heuristic_map(seeker: Seeker):
#         """
#             set up heuristic map of the seeker (seeker.heuristic_map)

#             returns nothing
#         """
#         from copy import deepcopy
#         seeker.heuristic_map = deepcopy(seeker.skelaton_map)
#         seeker.vision()
#         pos_r, pos_c = seeker.coordinate
#         mark_hider = []         # mark all hiders in the vision
#         mark_announcement = []  # mark all announcements in the vision

#         # traverse seeker.vision_map
#         for idrow in range(-seeker.radius, seeker.radius + 1, +1):
#             # idrow in [-radius, radius + 1)
#             if idrow < 0:
#                 continue
#             if idrow >= len(seeker.vision_map):
#                 break
#             for idcol in range(-seeker.radius, seeker.radius + 1, +1):
#                 # idcol in [-radius, radius + 1)
#                 if idcol < 0:
#                     continue
#                 if idcol >= len(seeker.vision_map[0]):
#                     break
#                 if seeker.vision_map[idrow][idcol] == True:
#                     cell = seeker.origin_map[idrow][idcol]
#                     if -1 in cell:
#                         # is wall
#                         if len(cell) > 1:
#                             # exists announcement(s) on this wall
#                             seeker.heuristic_map[idrow][idcol] = 0
#                         else:
#                             seeker.heuristic_map[idrow][idcol] = 1000
#                     elif 1000 in cell:
#                         # empty cell
#                         if cell != [1000]:
#                             # invalid map!
#                             raise ValueError("An empty cell cannot contain any objects")
#                         seeker.heuristic_map[idrow][idcol] = 1000
#                     else:
#                         # list has only Hider - Seeker - Announcement object
#                         for component in cell:
#                             # have not done
                            
#                 # else, heuristic value of the corresponding cell remains unchanged

#     def run(self):
#         nhiders = len(self.problem.hiders)
#         seeker = self.problem.seeker
#         reached = {
#             seeker.coordinate: Node(
#                 id_row=seeker.coordinate[0],
#                 id_col=seeker.coordinate[1],
#                 cumulative_pathcost=0,
#                 parent=None
#             )
#         }
        
#         frontier = PriorityQueue( () )

#         while len(frontier) > 0:
#             pass

lv1 = Level1('test/map1_1.txt')
# lv1.run()