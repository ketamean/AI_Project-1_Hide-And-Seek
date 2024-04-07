from player import *
class StateForFE:
    """
        this class keeps all steps that all agents have gone
    """
    _all_states = [] # list of states
    _cnt_state = 0
    def __init__(self, player: Hider | Seeker, old_row: int, old_col: int, new_row: int, new_col: int, announcements: list) -> None:
        """
            args:
                player: the player object from which we can get the signature, id (if it is a Hider),...
                announcements: list of coordinate of announcements in the game board
        """
        from copy import deepcopy
        self.player = player                        # player's signature (Hider or Seeker)
        self.old_coordinate = (old_row, old_col)
        self.new_coordinate = (new_row, new_col)
        self.vision = deepcopy(player.vision_map)
        self.announcement = deepcopy(announcements) # list of announcements' coordinate
        # add this new state to the list of states
        StateForFE._all_states.append( self )

    @staticmethod
    def reset():
        StateForFE._all_states = []
        StateForFE._cnt_state = 0
    
    @staticmethod
    def get():
        """
            UI class may require to get all the states sequentially. This method will help UI do this

            If there is a state in the list to be returned, it will return an object; otherwise, returns None

            `None` just means there is no more state in the list and sometimes cannot be treated as a flag that marks the end point of the searching process
        """
        if StateForFE._cnt_state < 0:
            raise ValueError("StateForFE._cnt_state < 0 ?????")
        if StateForFE._cnt_state >= len(StateForFE._all_states):
            return None
        
        StateForFE._cnt_state += 1
        return StateForFE._all_states[ StateForFE._cnt_state - 1 ]