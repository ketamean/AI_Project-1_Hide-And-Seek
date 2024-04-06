"""
    this file includes Hider class and Seeker class
"""
from state import *

# abstract method
class Player:
    def __init__(self, coordinate: tuple, radius: int, h) -> None:
        """
            there are 3 kinds of map:
            - original map: = problem.map_list
            - map of vision: currently viewable cells, not cumulatively
                + False for unviewable cells (and walls without announcement)
                + True for viewable cells (and walls within announcement)
            - map of heuristic: heuristics value only (-1, 0-999, 1000)
        """
        self.coordinate = coordinate    
        self.signature = 'Hider'
        self.radius = radius            # field of view
        self.latest_states = []         # list of some latest (or all) State object
        self.origin_map = None
        self.vision_map = None
        self.heuristic_map = None
        self.skeleton_map = None        # skeleton map which includes walls only
                                        # -1 for walls, 1000 for empty cells

    # def result(self, origin_state: State, action: str, map: list):
    #     """
    #         change the map according to the given action
    #         returns the new map
    #     """
    #     cur_r, cur_c = self.coordinate
        
    #     # get current cummulative path cost

    #     if action == 'U':
    #         new_r, new_c = cur_r - 1, cur_c
    #     elif action == 'D':
    #         new_r, new_c = cur_r + 1, cur_c
    #     elif action == 'L':
    #         new_r, new_c = cur_r, cur_c - 1
    #     elif action == 'R':
    #         new_r, new_c = cur_r, cur_c + 1
    #     elif action == 'UL':
    #         new_r, new_c = cur_r - 1, cur_c - 1
    #     elif action == 'UR':
    #         new_r, new_c = cur_r - 1, cur_c + 1
    #     elif action == 'DL':
    #         new_r, new_c = cur_r + 1, cur_c - 1
    #     elif action == 'DR':
    #         new_r, new_c = cur_r + 1, cur_c + 1
    #     else:
    #         raise ValueError("Wrong action was given!")
    #     new_g = origin_state.g + 1
    #     new_h = 
    #     self.latest_states.append(
    #         State(
    #             coordinate_from=(cur_r, cur_c),
    #             coordinate_to=(new_r, new_c),
    #             g= new_g,
    #             h= new_h,
    #             f= new_g + new_h
    #         )
    #     )

    def __vision_col(self):
        r,c = self.coordinate
        # traverse the left half of the column of player
        flag_meetwall = False
        for idcol in range(c - 1, c - self.radius - 1, -1):
            if idcol < 0:
                break
            if flag_meetwall:
                if -1 in self.origin_map[r][idcol]:
                    # is wall
                    self.vision_map[r][idcol] = True
                else:
                    self.vision_map[r][idcol] = False
                continue
            if -1 in self.origin_map[r][idcol]:
                flag_meetwall = True
            self.vision_map[r][idcol] = True

        # traverse the right half of the column of player
        flag_meetwall = False
        for idcol in range(c + 1, c + self.radius + 1, + 1):
            if idcol >= len(self.origin_map[0]):
                break
            if flag_meetwall:
                if -1 in self.origin_map[r][idcol]:
                    self.vision_map[r][idcol] = True
                else:
                    self.vision_map[r][idcol] = False
                continue
            if -1 in self.origin_map[r][idcol]:
                flag_meetwall = True
            self.vision_map[r][idcol] = True

    def __vision_row(self):
        r,c = self.coordinate
        # traverse the upper half of the column of player
        flag_meetwall = False
        for idrow in range(r - 1, r - self.radius - 1, -1):
            if idrow < 0:
                break
            if flag_meetwall:
                if -1 in self.origin_map[idrow][c]:
                    self.vision_map[idrow][c] = True
                else:
                    self.vision_map[idrow][c] = False
                continue
            
            if -1 in self.origin_map[idrow][c]:
                flag_meetwall
                flag_meetwall = True
            self.vision_map[idrow][c] = True

        # traverse the lower half of the column of player
        flag_meetwall = False
        for idrow in range(r + 1, r + self.radius + 1, +1):
            if idrow >= len(self.origin_map):
                break
            if flag_meetwall:
                if -1 in self.origin_map[idrow][c]:
                    self.vision_map[idrow][c] = True
                else:
                    self.vision_map[idrow][c] = False
                continue
            
            if -1 in self.origin_map[idrow][c]:
                flag_meetwall = True
            self.vision_map[idrow][c] = True

    def __vision_main_diagonal(self):
        r,c = self.coordinate
        # traverse the upper half of the column of player
        flag_meetwall = False
        for idrow in range(r - 1, r - self.radius - 1, -1):
            if idrow < 0:
                break
            if c - r+idrow < 0:
                continue
            if c - r+idrow >= len(self.origin_map[0]):
                break
            if flag_meetwall:
                if -1 in self.origin_map[idrow][c - r+idrow]:
                    self.vision_map[idrow][c - r+idrow] = True
                else:
                    self.vision_map[idrow][c - r+idrow] = False
                continue
            
            if -1 in self.origin_map[idrow][c - r+idrow]:
                flag_meetwall = True
            self.vision_map[idrow][c - r+idrow] = True

        # traverse the lower half of the column of player
        flag_meetwall = False
        for idrow in range(r + 1, r + self.radius + 1, + 1):
            if idrow >= len(self.origin_map):
                break
            if c - r+idrow < 0:
                continue
            if c - r+idrow >= len(self.origin_map[0]):
                break
            if flag_meetwall:
                if -1 in self.origin_map[idrow][c - r+idrow]:
                    self.vision_map[idrow][c - r+idrow] = True
                else:
                    self.vision_map[idrow][c - r+idrow] = False
                continue
            
            if -1 in self.origin_map[idrow][c - r+idrow]:
                flag_meetwall = True
            self.vision_map[idrow][c - r+idrow] = True

    def __vision_sub_diagonal(self):
        r,c = self.coordinate
        # traverse the upper half of the column of player
        flag_meetwall = False
        for idrow in range(r - 1, r - self.radius - 1, -1):
            if idrow < 0:
                break
            if c + r-idrow < 0:
                break
            if c + r-idrow >= len(self.origin_map[0]):
                continue
            if flag_meetwall:
                if -1 in self.origin_map[idrow][c + r-idrow]:
                    self.vision_map[idrow][c + r-idrow] = True
                else:
                    self.vision_map[idrow][c + r-idrow] = False
                continue
            
            if -1 in self.origin_map[idrow][c + r-idrow]:
                flag_meetwall = True
            self.vision_map[idrow][c + r-idrow] = True

        # traverse the lower half of the column of player
        flag_meetwall = False
        for idrow in range(r + 1, r + self.radius + 1, + 1):
            if idrow >= len(self.origin_map):
                break
            if c + r-idrow < 0:
                break
            if c + r-idrow >= len(self.origin_map[0]):
                continue
            if flag_meetwall:
                if -1 in self.origin_map[idrow][c + r-idrow]:
                    self.vision_map[idrow][c + r-idrow] = True
                else:
                    self.vision_map[idrow][c + r-idrow] = False
                continue
            
            if -1 in self.origin_map[idrow][c + r-idrow]:
                flag_meetwall = True
            self.vision_map[idrow][c + r-idrow] = True

    def __vision_topleft_quarter(self):
        r,c = self.coordinate
        # below main diagonal
        # x: horizontal - right to left
        # y: vertical - bottom up
        for idcol in range(c - 2, c - self.radius - 1, -1):
            if idcol < 0:
                break
            for idrow in range(r - 1, r - c+idcol, -1):
                if idrow < 0:
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = c - idcol
                y1 = r - idrow
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if c - x0 < 0 or r - y0 < 0:
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r - y0][c - x0]:
                            # wall
                            self.vision_map[r - y0][c - x0] = True
                        else:
                            self.vision_map[r - y0][c - x0] = False
                    else:
                        if -1 in self.origin_map[r - y0][c - x0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r - y0][c - x0] = True
                        
        # above main diagonal
        # x: vertical - bottom up
        # y: horizontal - right to left
        for idrow in range(r - 2, r - self.radius - 1, -1):
            if idrow < 0:
                break
            for idcol in range(c - 1, c - r+idrow, -1):
                if idcol < 0:
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = r - idrow
                y1 = c - idcol
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if r - x0 < 0 or c - y0 < 0:
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r - x0][c - y0]:
                            self.vision_map[r - x0][c - y0] = True
                        else:
                            self.vision_map[r - x0][c - y0] = False
                    else:
                        if -1 in self.origin_map[r - x0][c - y0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r - x0][c - y0] = True

    def __vision_topright_quarter(self):
        r,c = self.coordinate
        # below sub diagonal
        # x: horizontal - left to right
        # y: vertical - bottom up
        for idcol in range(c + 2, c + self.radius + 1, +1):
            if idcol >= len(self.origin_map[0]):
                break
            for idrow in range(r - 1, r + c-idcol, -1):
                if idrow < 0:
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = idcol - c
                y1 = r - idrow
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if c + x0 >= len(self.origin_map[0]) or r - y0 < 0:
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r - y0][c + x0]:
                            self.vision_map[r - y0][c + x0] = True
                        else:
                            self.vision_map[r - y0][c + x0] = False
                    else:
                        if -1 in self.origin_map[r - y0][c + x0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r - y0][c + x0] = True

        # above sub diagonal
        # x: vertical - bottom up
        # y: horizontal - right to left
        for idrow in range(r - 2, r - self.radius - 1, -1):
            if idrow < 0:
                break
            for idcol in range(c + 1, c + r-idrow, +1):
                if idcol >= len(self.origin_map[0]):
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = r - idrow
                y1 = idcol - c
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if r - x0 < 0 or c + y0 >= len(self.origin_map[0]):
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r - x0][c + y0]:
                            self.vision_map[r - x0][c + y0] = True
                        else:
                            self.vision_map[r - x0][c + y0] = False
                    else:
                        if -1 in self.origin_map[r - x0][c + y0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r - x0][c + y0] = True
        

    def __vision_botleft_quarter(self):
        r,c = self.coordinate
        # above sub diagonal
        # x: horizontal - right to left
        # y: vertical - top down
        for idcol in range(c - 2, c - self.radius - 1, -1):
            if idcol < 0:
                break
            for idrow in range(r + 1, r + c - idcol, +1):
                if idrow >= len(self.origin_map):
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = c - idcol
                y1 = idrow - r
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if c - x0 < 0 or r + y0 >= len(self.origin_map):
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r + y0][c - x0]:
                            self.vision_map[r + y0][c - x0] = True
                        else:
                            self.vision_map[r + y0][c - x0] = False
                    else:
                        if -1 in self.origin_map[r + y0][c - x0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r + y0][c - x0] = True

        # below sub diagonal
        # x: vertical - top down
        # y: horizontal - right to left
        for idrow in range(r + 2, r + self.radius + 1, +1):
            if idrow >= len(self.origin_map):
                break
            for idcol in range(c - 1, c + r - idrow, -1):
                if idcol < 0:
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = idrow - r
                y1 = c - idcol
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if r + x0 >= len(self.origin_map) or c - y0 < 0:
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r + x0][c - y0]:
                            self.vision_map[r + x0][c - y0] = True
                        else:
                            self.vision_map[r + x0][c - y0] = False
                    else:
                        if -1 in self.origin_map[r + x0][c - y0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r + x0][c - y0] = True

    def __vision_botright_quarter(self):
        r,c = self.coordinate
        # above sub diagonal
        # x: horizontal - left to right
        # y: vertical - top down
        for idcol in range(c + 2, c + self.radius + 1, +1):
            if idcol >= len(self.origin_map[0]):
                break
            for idrow in range(r + 1, r + idcol - c, +1):
                if idrow >= len(self.origin_map):
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = idcol - c
                y1 = idrow - r
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if c + x0 >= len(self.origin_map[0]) or r + y0 >= len(self.origin_map):
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r + y0][c + x0]:
                            self.vision_map[r + y0][c + x0] = True
                        else:
                            self.vision_map[r + y0][c + x0] = False
                    else:
                        if -1 in self.origin_map[r + y0][c + x0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r + y0][c + x0] = True

        # below sub diagonal
        # x: vertical - top down
        # y: horizontal - left to right
        for idrow in range(r + 2, r + self.radius + 1, +1):
            if idrow >= len(self.origin_map):
                break
            for idcol in range(c + 1, c + idrow - r, +1):
                if idcol >= len(self.origin_map[0]):
                    break
                if isinstance(self.vision_map[idrow][idcol], bool):
                    # already determined
                    continue
                x0 = 0
                y0 = 0
                x1 = idrow - r
                y1 = idcol - c
                if x1 == 0 and y1 == 0:
                    continue
                dx = x1
                dy = y1
                D = dy - 0.5*dx
                meet_wall = False
                for i in range(self.radius):
                    if D > 0:
                        x0 += 1
                        y0 += 1
                        D = dy - dx
                    else:
                        x0 += 1
                        D = dy
                    if r + x0 >= len(self.origin_map) or c + y0 >= len(self.origin_map[0]):
                        break
                    if meet_wall:
                        if -1 in self.origin_map[r + x0][c + y0]:
                            self.vision_map[r + x0][c + y0] = True
                        else:
                            self.vision_map[r + x0][c + y0] = False
                    else:
                        if -1 in self.origin_map[r + x0][c + y0]:
                            # wall
                            meet_wall = True
                        self.vision_map[r + x0][c + y0] = True
    def vision(self):
        """
            reset self.vision_map and define new viewable cells

            returns nothing
        """
        from copy import deepcopy
        self.vision_map = deepcopy(self.skeleton_map)
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

class State:
    """
        each state keeps the coordinate of a particular cell in the map, g, h, f (where h = Manhattan distance heuristic, g = cummulative path cost, f = g + h)
        
        note that, a cell can appear in multiple different states

        this is an auxiliary class for BE (solving problem in levels).
        for each player object (Hider or Seeker), there is a list that contains all the states (or optimally N latest state)
    """
    def __init__(self, coordinate_from: tuple, coordinate_to: tuple, player: Player) -> None:
        self.from_row, self.from_col = coordinate_from
        self.to_row, self.to_col = coordinate_to
        self.player = player

class Hider(Player):
    """
        each instance of the class represents a hider.

        there are possibly multiple hiders in a game so that hiders are differentiated by their IDs (numberred from 1)

        there is an attribute called self.signature (a string) used to distinguish between a Hider and a Seeker. For a hider, signature = 'Hider' (with capitalized H)

        hider keeps a skeleton version of the map, which is the map in the pov of the hider (already known walls)
    """
    _cnt = 0        # count for ID
    def __init__(self, coordinate: tuple, radius = 3, step_to_announcement = 5) -> None:
        """
            coordinate: tuple (id_row, id_col) of the hider in the above map
            id of the hider will be automatically calculated when it was initialized. When you reset the game, you need to reset the id counter (which is a static attribute) Hider._cnt using the static method Hider.reset_id_counter()
        """
        from copy import deepcopy
        super().__init__(coordinate=coordinate, radius=radius, h = None)
        self.id = Hider._cnt            # id of the hider to differentiate hiders
                                        # also the id of hider in list Problem.hiders
        Hider._cnt += 1
        self.step_to_announcement = step_to_announcement        # number of steps between 2 announcements           
        self.count_to_announcement = 0  # if == 0, raise an announcement reset to step_to_announcement 

        self.frontier = {
            # pairs of (idrow, idcol): node
        }

        self.reached = [
            # list of (idrow, idcol)
        ]
    
    @staticmethod
    def reset_id_counter():
        Hider._cnt = 0
    
    def announce(self):
        """
            raise an announcement randomly

            return the announcement object, and you MUST put it in the map
        """
        from random import randint
        cur_r, cur_c = self.coordinate
        lwr_r, upr_r = self.coordinate  # lower bound and upper bound of row idx
        lwr_c, upr_c = self.coordinate  # lower bound and upper bound of col idx
        for i in range(cur_r-self.radius, cur_r + 1, +1):
            lwr_r = i
            if lwr_r >= 0:
                break
        for i in range(cur_r+self.radius, cur_r - 1, -1):
            upr_r = i
            if upr_r < len(self.origin_map):
                break
        for i in range(cur_c-self.radius, cur_c + 1, +1):
            lwr_c = i
            if lwr_c >= 0:
                break
        for i in range(cur_c+self.radius, cur_c - 1, -1):
            upr_c = i
            if upr_c < len(self.origin_map[0]):
                break
        while True:
            r,c = randint(lwr_r, upr_r), randint(lwr_c, upr_c)
            if self.skeleton_map[r][c] != -1:
                break
        res = Announcement(
            coordinate=(r,c),
            hider=self
        )
        if 1000 in self.origin_map[r][c]:
            # empty cell
            self.origin_map[r][c] = [ res ]
        else:
            # non-empty cell
            self.origin_map[r][c].append( res )
            
        return res

    @staticmethod
    def move_obstacles(map: list, obstacles: list):
        """
            args:
                map: the map read from the input file
                    -1: wall
                    2: hider
                    3: seeker
                    1000: anempty cell
                obstacles: a list of Obstacle objects in the above map

            hiders are allowed to move obstacles at the beginning of the game
            this method will optimally alter the position of all obstacles.
            after that, places that were occupied by obstacles will be considered as walls (and these cells in the list will be set to -1)

            returns the new map
        """
        pass

    def action(self, map: list):
        """
            choose one of 8 directions to go on
            return the action as a string
                'U' (up), 'D' (down), 'L' (left), 'R' (right),
                'UL' (up left), 'UR' (up right), 'DL' (down left), 'DR' (down right)
        """
        pass

    def result(self, origin_state: State, action: str, map: list):
        """

        """
        pass
    
class Announcement:
    """
        an announcement raised by a hider
    """
    def __init__(self, coordinate: tuple, hider: Hider) -> None:
        """
            coordinate: position of the announcement in the map (idrow, idcol)
            hider: the hider who raised this announcement
        """
        self.coordinate = coordinate
        self.hider = hider
        self.signature = 'Announcement'

class Seeker(Player):
    """
        each instance of the class represents the seeker

        although the seeker is unique in the game, this class was NOT designed to be in singleton pattern

        there is an attribute called self.signature (a string) used to distinguish between a Hider and a Seeker. For a seeker, signature = 'Seeker' (with capitalized S)

        seeker keeps a skeleton version of the map, which is the map in the pov of the seeker (already known walls)
    """
    def __init__(self, coordinate: tuple, radius = 3) -> None:
        """
            coordinate: tuple (id_row, id_col) of the hider in the map
        """
        super().__init__(coordinate=coordinate, radius=radius, h = None)
        self.signature = 'Seeker'
        self.score = 0                  # score of the seeker, initially 0
        

    def action(self, map: list):
        """
            choose one of 8 directions to go on
            return the action as a string
                'U' (up), 'D' (down), 'L' (left), 'R' (right),
                'UL' (up left), 'UR' (up right), 'DL' (down left), 'DR' (down right)
        """
        pass

    def result(self, origin_state: State, action: str, map: list):
        """
            change the map according to the given action

            then coordinate and score of the Seeker will be changed; a new state will be added to the list of states

            returns the new map
        """
        map = super().result(origin_state=origin_state, action=action, map=map)
