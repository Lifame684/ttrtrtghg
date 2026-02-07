import random
from typing import List
from .card import Card, Suit, Rank

class Deck:
    def __init__(self):
        self.cards: List[Card] = [
            Card(rank, suit)
            for rank in Rank
            for suit in Suit
        ]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> List[Card]:
        drawn = []
        for _ in range(count):
            if self.cards:
                drawn.append(self.cards.pop())
        return drawn

    def __len__(self):
        return len(self.cards)
