from player import *
from obstacle import *

class Problem:
    """
        The map of the game has size m x n (m rows, n columns). Each element is denoted by one of the following notations (each of which is either an integer or an object of Hider/Seeker)
            - minus 1s (or -1) represent walls (non-movable). Cells that initially are obstacles will be static in the game and thus will be considered as walls
            - Seeker object: the unique seeker, signature = 'Seeker'
            - Hider objects: hiders, signature = 'Hider'
            - Announcement objects: announcement of a hider, signature = 'Announcement'
            - non-negative INTEGERS: heuristic values (initially extremely large, 1000), represent blank cells

            If there are multiple components in a cell (multiple Hiders, or wall + announcement), they will be combined to be in a list
            A cell which is a wall is either -1 or list of [-1, Announcement-object]

        e.g.,
        (
            (-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1),
            (-1,<Seeker>,1e9+7,1e9+7,3,2,1,2,2,1,2,-1),
            (-1,-1,-1,1e9+7,2,1,<Hider>,1,1,<Hider>,1,-1),
            (-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1)
        )
    """
    def __parse_map(self, lines: list) -> list:
        """
            read the map from the given input file (the file was splited into lines)
            obtain the map in terms of a list
        """
        self.map_list = []
        nrow, ncol = lines[0].split(sep=' ')

        self.hiders_coor = []
        for i in range(nrow):
            nums = lines[1 + i].split(sep=' ')
            row = []
            for j in range(ncol):
                n = int(nums[j])
                if n == 0:
                    # empty
                    row.append(1000)
                elif n == 1:
                    # wall
                    row.append(-1)
                elif n == 2:
                    # hider
                    self.hiders_coor.append( (i,j) )
                    row.append(2)
                elif n == 3:
                    # seeker
                    self.seeker_coor = (i,j)
                    row.append(3)
            self.map_list.append( row )

    def __parse_input_file(self, buffer):
        lines = buffer.splitlines()
        nrow, ncol = lines[0].split(sep=' ')
        self.__parse_map(lines=lines)

        # list of coordinates of obstacles
        self.obstacles = []
        groups = lines[1 + nrow].split(' ')
        cnt = 0
        r_topleft = 0
        c_topleft = 0
        r_botright = 0
        c_botright = 0
        for row in lines[1 + nrow::]:
            r_topleft, c_topleft, r_botright, c_botright = row
            self.obstacles.append(
                Obstacle(
                    r_topleft, c_topleft,
                    r_botright, c_botright
                )
            )

    def __init__(self, input_filename: str, allow_move_obstacles: bool) -> None:
        """
            input_filename: the file that contains the initial map. The file must be in the correct format
                - The first line includes 2 positive integers N M (separated by a single space). The first number is number of rows, while the second one is number of columns
                - The next N lines is the map, each of which contains M integers. These integers are also separated by single spaces
                - The last line includes 4*k non-negative integers (separated by single spaces), divided into k groups, each of which in the format (id_row_topleft, id_col_topleft, id_row_bottomright, id_col_bottomright)
            goal_checker: a function f(State) that returns True if the given state is the goal state; otherwise, returns False
        """
        """
            map_list: 2d array as the map. -1s represent walls, a unique Seeker object, possibly multiple (can be 1 or more) Hider objects
        """
        self.seeker = None  # the unique Seeker object
        self.hiders = []    # list of Hider objects
        with open(input_filename, 'r') as f:
            buffer = f.read()

            """
                parse input file to get
                - self.seeker_coor: tuple, (idrow, idcol)
                - self.hiders_coor: list of tuples
                - self.obstacles: list of Obstacle objects
            """
            self.__parse_input_file(buffer=buffer)
        
        if allow_move_obstacles:
            # let hiders move obstacles
            self.map_list = Hider.move_obstacles(map=self.map_list, obstacles=self.obstacles)
        else:
            # not allowed to move obstacles => all obstacles are instantly set to walls
            for obstacle in self.obstacles:
                for i in range(obstacle.id_row_topleft, obstacle.id_row_botright + 1):
                    for j in range(obstacle.id_col_topleft, obstacle.id_col_botright + 1):
                        self.map_list[i][j] = -1

        # now the map is static
        # assign Hider and Seeker objects to the map
        _r,_c = self.seeker_coor
        self.seeker = Seeker(coordinate=(_r,_c))
        self.map_list[_r][_c] = self.seeker
        for (r,c) in self.hiders_coor:
            hider = Hider(coordinate=(r,c))
            self.hiders.append( hider )
            self.map_list[r][c] = hider
        
        del self.seeker_coor
        del self.hiders_coor

    def action(self, player: Hider | Seeker):
        """
            state: the state from that an action will be taken
            player: the object that will move away from its current position
            there are 8 actions, given as strings:
                'U' (up), 'D' (down), 'L' (left), 'R' (right),
                'UL' (up left), 'UR' (up right), 'DL' (down left), 'DR' (down right)
            returns a list of actions that possibly be done
        """
        pass
    
    def result(self, origin_state: State, action: str, player: Hider | Seeker, h: function):
        """
            applying the given action to the origin state

            arg h: a function to calculate heuristic value at the current level, given by developers

            change both map of the current instance problem and the map in pov of the player
        """
        idrow, idcol = player.coordinate
        if action == 'U':
            pass
        elif action == 'D':
            pass
        elif action == 'L':
            pass
        elif action == 'R':
            pass
        elif action == 'UL':
            pass
        elif action == 'UR':
            pass
        elif action == 'DL':
            pass
        elif action == 'DR':
            pass