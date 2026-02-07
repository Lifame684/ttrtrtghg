from game.player import Player
from core.evaluator import Evaluator
from .strategies import Strategy

import random

class PokerBot(Player):
    def __init__(self, name: str, stack: int, style="balanced", difficulty="medium", avatar_id: int = 0):
        super().__init__(name, stack, avatar_id)
        self.style = style
        self.difficulty = difficulty

    def decide_action(self, table_current_bet: int, community_cards, pot_size: int):
        # Сложность влияет на частоту случайных действий
        randomness_map = {"easy": 0.25, "medium": 0.1, "hard": 0.02}
        if random.random() < randomness_map.get(self.difficulty, 0.1):
            # Случайное действие (Блеф или Глупый Фолд)
            rand_val = random.random()
            if rand_val < 0.3: return ("fold", 0)
            if rand_val < 0.8: return ("call", max(0, table_current_bet - self.current_bet))
            return ("raise", (table_current_bet - self.current_bet) + 50)

        hand_power, _ = Evaluator.evaluate(self.hand + community_cards)
        needed_to_call = table_current_bet - self.current_bet
        
        action, amount = Strategy.get_action(
            self.style, 
            hand_power, 
            needed_to_call, 
            self.stack, 
            pot_size
        )
        
        # Ensure we don't bet more than we have
        if amount > self.stack:
            amount = self.stack
            
        return action, amount
