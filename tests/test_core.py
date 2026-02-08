import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from core.card import Card, Rank, Suit
from core.deck import Deck
from core.evaluator import Evaluator, HandRank

def test_deck():
    deck = Deck()
    assert len(deck) == 52
    print("Deck test passed!")

def test_evaluator():
    # Pair
    hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.CLUBS), Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.TWO, Suit.SPADES), Card(Rank.THREE, Suit.DIAMONDS), Card(Rank.FOUR, Suit.CLUBS)]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.PAIR
    assert kickers == [14, 13, 10, 4]

    # Two Pair
    hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS), Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.TWO, Suit.SPADES), Card(Rank.THREE, Suit.DIAMONDS)]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.TWO_PAIR
    assert kickers == [14, 13, 10]

    # Three of a Kind
    hand = [Card(Rank.TEN, Suit.SPADES), Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.KING, Suit.SPADES), Card(Rank.TWO, Suit.DIAMONDS), Card(Rank.THREE, Suit.CLUBS)]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.THREE_OF_A_KIND
    assert kickers == [10, 14, 13]

    # Straight
    hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS), Card(Rank.THREE, Suit.CLUBS), Card(Rank.FOUR, Suit.DIAMONDS), Card(Rank.FIVE, Suit.SPADES), Card(Rank.KING, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.CLUBS)]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.STRAIGHT
    assert kickers == [5]

    # Flush
    hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.SPADES), Card(Rank.FIVE, Suit.SPADES), Card(Rank.TWO, Suit.SPADES), Card(Rank.KING, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.CLUBS)]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.FLUSH
    assert kickers == [14, 10, 7, 5, 2]

    # Straight Flush
    hand = [Card(Rank.TEN, Suit.SPADES), Card(Rank.NINE, Suit.SPADES), Card(Rank.EIGHT, Suit.SPADES), Card(Rank.SEVEN, Suit.SPADES), Card(Rank.SIX, Suit.SPADES), Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.KING, Suit.CLUBS)]
    rank, kickers = Evaluator.evaluate(hand)
    assert rank == HandRank.STRAIGHT_FLUSH
    assert kickers == [10]

    print("Evaluator all tests passed!")

if __name__ == "__main__":
    test_deck()
    test_evaluator()
