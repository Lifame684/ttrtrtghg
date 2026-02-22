from game.player import Player
from core.evaluator import Evaluator
from .strategies import Strategy

import random

class PokerBot(Player):
    def __init__(self, name: str, stack: int, style="balanced", difficulty="medium", avatar_id: int = 0):
        super().__init__(name, stack, avatar_id)
        self.style = style
        self.difficulty = difficulty

    def decide_action(self, table_current_bet: int, community_cards, pot_size: int, tournament_stage: str = "early", position: str = "BU"):
        # 1. Randomness (Difficulty)
        randomness_map = {"easy": 0.25, "medium": 0.1, "hard": 0.02}
        if random.random() < randomness_map.get(self.difficulty, 0.1):
            rand_val = random.random()
            if rand_val < 0.3: return ("fold", 0)
            if rand_val < 0.8: return ("call", max(0, table_current_bet - self.current_bet))
            return ("raise", (table_current_bet - self.current_bet) + 50)

        # 2. Hand Evaluation
        hand_power, _ = Evaluator.evaluate(self.hand + community_cards)
        needed_to_call = table_current_bet - self.current_bet
        
        # 3. Board Texture Analysis
        board_texture = "dry"
        if len(community_cards) >= 3:
            suits = [c.suit for c in community_cards]
            ranks = sorted([c.rank.value for c in community_cards])
            # Check for flush draws or straight draws on board
            if any(suits.count(s) >= 3 for s in set(suits)):
                board_texture = "wet"
            for i in range(len(ranks) - 2):
                if ranks[i+2] - ranks[i] <= 3: # Close ranks
                    board_texture = "wet"

        # 4. ICM & Tournament Stage Adjustments
        eff_style = self.style
        if tournament_stage in ["bubble", "final_table"]:
            if self.stack < pot_size * 3:
                eff_style = "short_stack"
            else:
                if hand_power < 3: eff_style = "nit"

        # 5. Strategy Decision
        action, amount = Strategy.get_action(
            eff_style,
            hand_power, 
            needed_to_call, 
            self.stack, 
            pot_size,
            position=position,
            board_texture=board_texture
        )
        
        # Ensure we don't bet more than we have
        if amount > self.stack:
            amount = self.stack
            
        return action, amount
