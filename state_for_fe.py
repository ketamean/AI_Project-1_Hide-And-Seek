from player import *


class StateForFE:
    def __init__(self, seeker: Seeker, hiders: [Hider], announcements: list, score: int, is_end: bool) -> None:
        """
            args:
                player: the player object from which we can get the signature, id (if it is a Hider),...
                announcements: list xof coordinate of announcements in the game board
        """
        from copy import deepcopy
        self.hiders = deepcopy(hiders)  # player's signature (Hider or Seeker)
        self.seeker = deepcopy(seeker)
        self.announcement = deepcopy(announcements)  # list of announcements' coordinate
        self.score = deepcopy(score)
        self.is_end = deepcopy(is_end)
