from player import *

class State:
    """
        each state keeps the coordinate of a particular cell in the map, g, h, f (where h = Manhattan distance heuristic, g = cummulative path cost, f = g + h)
        
        note that, a cell can appear in multiple different states

        this is an auxiliary class for BE (solving problem in levels).
        for each player object (Hider or Seeker), there is a list that contains all the states (or optimally N latest state)
    """
    def __init__(self, coordinate_from: tuple, coordinate_to: tuple, player: Hider | Seeker, g:int, h: int, f: int) -> None:
        self.from_row, self.from_col = coordinate_from
        self.to_row, self.to_col = coordinate_to
        self.player = player
        self.g = g
        self.h = h
        self.f = f if f else self.g + self.h