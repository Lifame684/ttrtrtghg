from typing import List, Tuple
from .player import Player

class Tournament:
    def __init__(self, blind_structure=None, ante_type="none"):
        self.levels = blind_structure or [
            (10, 20, 0), (20, 40, 0), (40, 80, 0),
            (100, 200, 20), (200, 400, 40),
            (500, 1000, 100), (1000, 2000, 200)
        ]
        self.current_level_idx = 0
        self.hands_played = 0
        self.hands_per_level = 10
        self.ante_type = ante_type

    def get_current_level(self) -> Tuple[int, int, int]:
        return self.levels[self.current_level_idx]

    def on_hand_end(self, players: List[Player]) -> bool:
        self.hands_played += 1
        if self.hands_played >= self.hands_per_level:
            if self.current_level_idx < len(self.levels) - 1:
                self.current_level_idx += 1
                self.hands_played = 0
                return True
        return False

    def get_ante_to_pay(self, is_bb: bool) -> int:
        sb, bb, ante = self.get_current_level()
        if self.ante_type == "regular": return ante
        elif self.ante_type == "bb_ante": return bb if is_bb else 0
        return 0
