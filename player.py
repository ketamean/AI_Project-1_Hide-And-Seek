"""
    this file including Hider and Seeker class
"""
from map import *

class Hider:
    """
        each instance of the class represents a hider.

        there are possibly multiple hiders in a game so that hiders are differentiated by their IDs (numberred from 1)

        there is an attribute called self.signature (a string) used to distinguish between a Hider and a Seeker. For a hider, signature = 'Hider' (with capitalized H)
    """
    _cnt = 0    # 
    def __init__(self, map: Map, coordinate: tuple) -> None:
        """
            map: point to the map that the hider is in. When the hider moves, the map will be changed and the coordinate of the hider either
            coordinate: tuple (id_row, id_col) of the hider in the above map
            
            id of the hider will be automatically calculated when it was initialized. When you reset the game, you need to reset the id counter (which is a static attribute) Hider._cnt using the static method Hider.reset_id_counter()
        """
        Hider._cnt += 1
        self.id = Hider._cnt    # id of the hider to differentiate hiders
        self.map = map
        self.coordinate = coordinate
        self.signature = 'Hider'
    
    @staticmethod
    def reset_id_counter():
        Hider._cnt = 0

class Seeker:
    """
        each instance of the class represents the seeker

        although the seeker is unique in the game, this class was NOT designed to be in singleton pattern

        there is an attribute called self.signature (a string) used to distinguish between a Hider and a Seeker. For a seeker, signature = 'Seeker' (with capitalized S)
    """
    def __init__(self, map: Map, coordinate: tuple) -> None:
        """
            map: point to the map that the hider is in. When the hider moves, the map will be changed and the coordinate of the hider either
            coordinate: tuple (id_row, id_col) of the hider in the above map
        """
        self.map = map
        self.coordinate = coordinate
        self.signature = 'Seeker'
        self.steps = 0      # count number of steps that the hider has been moving, initially 0