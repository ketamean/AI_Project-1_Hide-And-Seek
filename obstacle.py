class Obstacle:
    """
        an instance of this class represents a moveable obstacle in the map.
        
        each obstacle is represented by coordinates of top-left and bottom-right cells


    """
    def __init__(self, id_r_topleft, id_c_topleft, id_r_botright, id_c_botright) -> None:
        """
            args: coordinate of top-left and bottom-right cells that the obstacle occupies
        """
        self.id_row_topleft = id_r_topleft
        self.id_col_topleft = id_c_topleft
        self.id_row_botright = id_r_botright
        self.id_col_botright = id_c_botright