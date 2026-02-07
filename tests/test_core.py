import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core.card import Card, Rank, Suit
from core.deck import Deck
from core.evaluator import Evaluator, HandRank

def test_deck():
    deck = Deck()
    assert len(deck) == 52
    cards = deck.draw(5)
    assert len(cards) == 5
    assert len(deck) == 47
    print("Deck test passed!")

def test_evaluator():
    # Проверка Пары
    hand = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.TEN, Suit.DIAMONDS),
        Card(Rank.TWO, Suit.SPADES)
    ]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.PAIR
    print("Evaluator test (Pair) passed!")

if __name__ == "__main__":
    test_deck()
    test_evaluator()
