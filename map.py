class Map:
    """
        this class keeps a 2d tuple as the map of the game of size m x n (m rows, n columns). Each element is denoted by 1 of the following notations (each of which is either an integer or an object of Hider/Seeker)
        - minus 2s (-2) represent walls (non-movable)
        - minus 1s (-1) represent obstacle (movable in high level)
        - Seeker object: the unique seeker, signature = 
        - Hider objects: hiders
        - non-negative INTEGERS: heuristic values (initially extremely large, 1000000007 = 1e9 + 7), represent blank cells

        e.g.,
        (
            (-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2),
            (-2,'x',1e9+7,1e9+7,1e9+7,1e9+7,1e9+7,1e9+7,1e9+7,1e9+7,1e9+7,-2),
            (-2,1e9+7,1e9+7,1e9+7,1e9+7,-1,'o',-1,-1,'o',1e9+7,-2),
            (-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2)
        )
    """
    def __init__(self, map: tuple) -> None:
        self.map = map