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
        # a frame to build vision of a player
        # cells in the vision are numbered from 0 to (2r+1)^2 - 1
        # the following list contains multiple sublists, each of which is at index i and is a sequence of cell numbers that become unviewable when the cell i is a wall
        Level2.__vision_convention = None
        self.problem = Problem(
            input_filename=input_filepath,
            allow_move_obstacles=False
        )
    
    @staticmethod
    def __init_heuristic(map:list, announcement: Announcement, player: Hider | Seeker):
        pass

    def vision(self, map: list, player: Hider | Seeker):
        """
            to obtain 2D matrix of size 2r+1 x 2r+1 which is the vision of the player

            if a cell is undefined (view is blocked), it will be denoted as 'x'; otherwise, it will be the same as the map_list

            returns the vision of the player object
        """
        res = []
        pos_r, pos_c = player.coordinate    # player (idrow, idcol)
        r = player.radius                   # radius
        # the top-left quater
        for i in range(pos_r - 1, pos_r - r - 1, -1):
            if i < 0:
                break
            for j in range(pos_c - 1, pos_c - r - 1, -1):
                if j < 0:
                    break

        # the top-right quater
        for i in range(pos_r - 1, pos_r - r - 1, -1):
            if i < 0:
                break
            for j in range(pos_c + 1, pos_c + r + 1, +1):
                if j < 0:
                    break

        for i in range(pos_r, pos_r + r + 1, +1):
            if i >= len(map):
                break
        

    def astar(self, problem: Problem):
        # only seeker moves
        seeker = problem.seeker

    def run(self, input_filepath: str):        
        n_hiders = len(self.problem.hiders)
        player_idx = -1

        # go step by step while there is a hider that has not been found
        while n_hiders:
            # get current player object (Hider/Seeker)
            # player_idx == -1 => Seeker
            # player_idx >= 0 => Hider = self.problem.hiders[ player_idx ]
            if player_idx == -1:
                cur_player = self.problem.seeker
            elif player_idx >= n_hiders:
                player_idx = -1
                continue
            else:
                cur_player = self.problem.hiders[ player_idx ]
            action = cur_player.action(self.problem.map_list)
            result = cur_player.result(
                action=action,
                map=self.problem.map_list
            )
