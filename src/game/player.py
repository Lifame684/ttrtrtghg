from typing import List
from core.card import Card

class Player:
    def __init__(self, name: str, stack: int, avatar_id: int = 0):
        self.name = name
        self.stack = stack
        self.avatar_id = avatar_id
        self.hand: List[Card] = []
        self.current_bet = 0
        self.is_active = True  # В игре ли (не сбросил ли карты)
        self.is_all_in = False

    def bet(self, amount: int):
        if amount >= self.stack:
            amount = self.stack
            self.is_all_in = True
        
        self.stack -= amount
        self.current_bet += amount
        return amount

    def reset_hand(self):
        self.hand = []
        self.current_bet = 0
        self.is_active = True
        self.is_all_in = False

    def __repr__(self):
        status = "ALL-IN" if self.is_all_in else ("FOLDED" if not self.is_active else f"Stack: {self.stack}")
        return f"Player({self.name}, {status}, Hand: {self.hand})"
