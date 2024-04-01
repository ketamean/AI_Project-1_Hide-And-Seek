"""
    this file includes Hider class and Seeker class
"""
class Hider:
    """
        each instance of the class represents a hider.

        there are possibly multiple hiders in a game so that hiders are differentiated by their IDs (numberred from 1)

        there is an attribute called self.signature (a string) used to distinguish between a Hider and a Seeker. For a hider, signature = 'Hider' (with capitalized H)

        hider keeps a skelaton version of the map, which is the map in the pov of the hider (already known walls)
    """
    _cnt = 0        # count for ID
    def __init__(self, coordinate: tuple, radius = 3, step_to_announcement = 5) -> None:
        """
            coordinate: tuple (id_row, id_col) of the hider in the above map
            id of the hider will be automatically calculated when it was initialized. When you reset the game, you need to reset the id counter (which is a static attribute) Hider._cnt using the static method Hider.reset_id_counter()
        """
        from copy import deepcopy
        Hider._cnt += 1
        self.id = Hider._cnt            # id of the hider to differentiate hiders
        self.coordinate = coordinate    
        self.signature = 'Hider'
        self.radius = radius            # field of view
        self.step_to_announcement = step_to_announcement        # number of steps between 2 announcements           
        self.count_to_announcement = self.step_to_announcement  # if == 0, raise an announcement reset to step_to_announcement 
    
    @staticmethod
    def reset_id_counter():
        Hider._cnt = 0
    
    def announce(self, map: list):
        """
            choose a sufficiently good position to raise an announcement

            return the coordinate (id_row, id_col) of the cell where announcement raised
        """
        pass
    
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

    def result(self, action: str, map: list):
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

class Seeker:
    """
        each instance of the class represents the seeker

        although the seeker is unique in the game, this class was NOT designed to be in singleton pattern

        there is an attribute called self.signature (a string) used to distinguish between a Hider and a Seeker. For a seeker, signature = 'Seeker' (with capitalized S)

        seeker keeps a skelaton version of the map, which is the map in the pov of the seeker (already known walls)
    """
    def __init__(self, coordinate: tuple, radius = 3) -> None:
        """
            coordinate: tuple (id_row, id_col) of the hider in the map
        """
        self.coordinate = coordinate
        self.signature = 'Seeker'
        self.score = 0                  # score of the seeker, initially 0
        self.radius = radius            # field of view


    def action(self, map: list):
        """
            choose one of 8 directions to go on
            return the action as a string
                'U' (up), 'D' (down), 'L' (left), 'R' (right),
                'UL' (up left), 'UR' (up right), 'DL' (down left), 'DR' (down right)
        """
        pass