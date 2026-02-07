class Tournament:
    def __init__(self, blind_structure=None):
        # Структура: (Small Blind, Big Blind)
        self.levels = blind_structure or [(10, 20), (20, 40), (40, 80), (100, 200), (200, 400)]
        self.current_level_idx = 0
        self.hands_played = 0
        self.hands_per_level = 10

    def get_current_blinds(self):
        return self.levels[self.current_level_idx]

    def on_hand_end(self):
        self.hands_played += 1
        if self.hands_played >= self.hands_per_level:
            if self.current_level_idx < len(self.levels) - 1:
                self.current_level_idx += 1
                self.hands_played = 0
                return True # Блайнды выросли
        return False
