from map import *
from player import *
class State:
    """
        this class is a state together with its additional information, such as coordinate of seeker, hiders, heuristic value,...
        states are differentiated by their corresponding maps.
    """
    def __init__(self, map: tuple, h, seeker = None, hiders = None) -> None:
        """
            map: 2d tuple
            h: heuristic value of the state
            seeker: Seeker object, is None in the initial state
            hiders: list of Hider object, is Node in the initial state

            >> Initiali state will not be given 2 arguments `seeker` and `hiders`. The after states implied from the previous state can inherit the seeker and hider list. From the second state, seeker and hiders MUST be given so that hider and seeker objects will not be regenerated.
        """

        if len(map) <= 0:
            raise ValueError("State.__init__: A map cannot be empty.")
        if not((seeker and hiders) or (not seeker and not hiders)):
            raise ValueError("State.__init__: arguments hider and seekers must be both given or both None.")
        self.map = Map(map=map)     # the 2d tuple of the map
        self.heuristic = h          # heuristic value
        self.seeker = seeker        # the Seeker object
        self.hiders = hiders        # list of Hider objects
        self.nrow = len(map)        # number of rows of the map
        self.ncol = len(map[0])     # number of columns of the map
        # =========================================================
        # get coordinate of seeker and list of coordinates of hiders for the initiali state when 2 argument `seeker` and `hiders` are both `None`
        if not seeker and not hiders:
            self.hiders = []
            # traverse the map
            for i in range(self.nrow):
                for j in range(self.ncol):
                    if not isinstance(map[i][j], int):
                        # not an int then must be a Seeker object or Hider object
                        if map[i][j].signature == 'Seeker':
                            # is seeker
                            self.seeker = Seeker(
                                map=map,
                                coordinate=(i,j)
                            )
                        elif map[i][j].signature == 'Hider':
                            # is hider
                            self.hiders.append(
                                Hider(
                                    map=map,
                                    coordinate=(i,j)
                                )
                            )