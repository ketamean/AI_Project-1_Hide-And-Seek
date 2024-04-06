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

        for row in seeker.vision_map:
            for cell in row:
                if cell == -1:
                    print('x', end=' ')
                elif cell == 1000:
                    print('-', end=' ')
                elif cell:
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print()
        

    def calculate_heuristic_1(self, pos_r: int, pos_c: int, seeker: Seeker):
        """
            calculate the value of heuristic in that state
            METHOD: NUMBER OF UNSEEN CELL
            return the heuristic value
        """
        mark_hider = []         # mark all hiders in the vision
        mark_announcement = []  # mark all announcements in the vision
        heuristics = 0

        # calculate unseen cell
        for idrow in range(pos_r - seeker.radius, pos_r + seeker.radius, +1):
            for idcol in range(pos_c - seeker.radius, pos_c + seeker.radius, +1):
                if idrow < 0 or idrow >= len(seeker.vision_map) or idcol < 0 or idcol >= len(seeker.vision_map[0]):
                    continue
                if self.seen_map[idrow][idcol] == False:
                    heuristics += 1
        return heuristics
    
    def update_seen_map(self, seeker: Seeker):
        """
            update the seen map of the seeker
        """
        from copy import deepcopy
        self.seen_map = deepcopy(self.skelaton_map)
        # 4 main lines
        self.__vision_row()
        self.__vision_col()
        self.__vision_main_diagonal()
        self.__vision_sub_diagonal()
        
        # other cells in 4 quarters
        self.__vision_topleft_quarter()
        self.__vision_topright_quarter()
        self.__vision_botleft_quarter()
        self.__vision_botright_quarter()

        r,c = self.coordinate
        self.vision_map[r][c] = True

    def update_vision_map(self, seeker: Seeker):
        """
            update the vision map of the seeker
            add the new vision to the dictionary
        """
        r, c = seeker.coordinate
        if (r,c) not in self.dict_vision:
            self.dict_vision[r,c] = seeker.vision_map

    def move_seeker(self, seeker: Seeker, action: str):
        idrow, idcol = seeker.coordinate
        if action == 'U':
            if idrow > 0 & seeker.skelaton_map[idrow - 1][idcol] != -1 and self.visited_map[idrow - 1][idcol] == False:
                # check if the cell is the previous state or not
                prev_row, prev_col = seeker.latest_states[len(seeker.latest_states) - 1]
                if prev_row != idrow - 1 or prev_col != idcol:
                    seeker.latest_states.append((idrow, idcol))
                    seeker.coordinate = (idrow - 1, idcol)
                    self.visited_map[idrow - 1][idcol] = True

    def a_star(self, seeker: Seeker, hiders: list[Hider]):
        announcement = []
        hider = hiders[0]
        r, c = seeker.coordinate
        r_hider, c_hider = hider.coordinate
        i = 0
        while (r != r_hider and c != c_hider and i < 5):
            i += 1
            r, c = seeker.coordinate
            self.update_seen_map(seeker)
            self.update_vision_map(seeker)
            self.visited_map[r][c] = True
            # calculate the heuristic value
            if r > 0 & self.seen_map[r - 1][c] == False & seeker.skelaton_map[r - 1][c] != -1:
                seeker.heuristic_map[r - 1][c] = self.calculate_heuristic_1(r - 1, c, seeker)
                print(seeker.heuristic_map[r - 1][c])
            if r < len(seeker.heuristic_map) - 1 & self.seen_map[r + 1][c] == False & seeker.skelaton_map[r + 1][c] != -1:
                seeker.heuristic_map[r + 1][c] = self.calculate_heuristic_1(r + 1, c, seeker)
            if c > 0 & self.seen_map[r][c - 1] == False & seeker.skelaton_map[r][c - 1] != -1:
                seeker.heuristic_map[r][c - 1] = self.calculate_heuristic_1(r, c - 1, seeker)
            if c < len(seeker.heuristic_map[0]) - 1 & self.seen_map[r][c + 1] == False & seeker.skelaton_map[r][c + 1] != -1:
                seeker.heuristic_map[r][c + 1] = self.calculate_heuristic_1(r, c + 1, seeker)
            if r > 0 & c > 0 & self.seen_map[r - 1][c - 1] == False & seeker.skelaton_map[r - 1][c - 1] != -1:
                seeker.heuristic_map[r - 1][c - 1] = self.calculate_heuristic_1(r - 1, c - 1, seeker)
            if r > 0 & c < len(seeker.heuristic_map[0]) - 1 & self.seen_map[r - 1][c + 1] == False & seeker.skelaton_map[r - 1][c + 1] != -1:
                seeker.heuristic_map[r - 1][c + 1] = self.calculate_heuristic_1(r - 1, c + 1, seeker)
            if r < len(seeker.heuristic_map) - 1 & c > 0 & self.seen_map[r + 1][c - 1] == False & seeker.skelaton_map[r + 1][c - 1] != -1:
                seeker.heuristic_map[r + 1][c - 1] = self.calculate_heuristic_1(r + 1, c - 1, seeker)
            if r < len(seeker.heuristic_map) - 1 & c < len(seeker.heuristic_map[0]) - 1 & self.seen_map[r + 1][c + 1] == False & seeker.skelaton_map[r + 1][c + 1] != -1:
                seeker.heuristic_map[r + 1][c + 1] = self.calculate_heuristic_1(r + 1, c + 1, seeker)

        for row in self.seen_map:
            for cell in row:
                # print(cell, end=' ')
                # if cell == -1:
                #     print('x', end=' ')
                # elif cell == 1000:
                #     print('-', end=' ')
                # else :
                #     print(cell, end=' ')
                if cell == True:
                    print(1, end=' ')
                else:
                    print(0, end=' ')
            print()

            # if len(heuristic) == 0:

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

        if nhiders == 1:
            self.a_star(seeker, self.problem.hiders)
        else:
            pass

class Node:
    def __init__(self, id_row: int, id_col: int, cumulative_pathcost: int, parent = None) -> None:
        # parent: parent node; is None if root node
        # coordinate: the state
        self.parent = parent
        self.coordinate = (id_row, id_col)
        self.h = 0
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
lv1.run()