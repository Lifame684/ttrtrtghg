import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from coach.analyzer import Coach, ActionGrade
from core.card import Card, Rank, Suit

def test_coach_preflop():
    # AA
    hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
    grade, comment, rec = Coach.analyze_preflop(hand, "fold", "BTN", 100, 1.0)
    print(f"AA fold: {grade}, rec: {rec}")
    assert grade == ActionGrade.BLUNDER
    assert rec == "raise"

    # 72o
    hand = [Card(Rank.SEVEN, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS)]
    grade, comment, rec = Coach.analyze_preflop(hand, "raise", "BTN", 100, 1.0)
    print(f"72o raise: {grade}, rec: {rec}")
    assert grade == ActionGrade.MISTAKE
    assert rec == "fold"

def test_coach_postflop():
    # Pair on low board
    hand = [Card(Rank.JACK, Suit.SPADES), Card(Rank.JACK, Suit.HEARTS)]
    community = [Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.SEVEN, Suit.CLUBS), Card(Rank.TWO, Suit.SPADES)]

    # Call small bet
    grade, comment, rec = Coach.analyze_postflop(hand, community, "call", 100, 1000)
    print(f"JJ call small: {grade}, rec: {rec}")
    assert grade == ActionGrade.GREAT

    # Call huge bet
    grade, comment, rec = Coach.analyze_postflop(hand, community, "call", 1000, 100)
    print(f"JJ call huge: {grade}, rec: {rec}")
    assert grade == ActionGrade.MISTAKE

if __name__ == "__main__":
    test_coach_preflop()
    test_coach_postflop()
