import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from game.player import Player
from game.table import Table
from core.card import Card, Rank, Suit

def test_side_pot_basic():
    p1 = Player("P1", 100); p2 = Player("P2", 1000); p3 = Player("P3", 1000)
    players = [p1, p2, p3]; table = Table(players)
    p1.hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
    p2.hand = [Card(Rank.KING, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
    p3.hand = [Card(Rank.TWO, Suit.SPADES), Card(Rank.THREE, Suit.HEARTS)]
    table.community_cards = [Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.TEN, Suit.HEARTS), Card(Rank.TEN, Suit.CLUBS), Card(Rank.TEN, Suit.SPADES), Card(Rank.TWO, Suit.DIAMONDS)]
    p1.total_contribution = 100; p1.is_active = True
    p2.total_contribution = 500; p2.is_active = True
    p3.total_contribution = 500; p3.is_active = True
    results = table.resolve_winners()
    p1_wins = sum(amt for p, amt, msg in results if p == p1)
    p2_wins = sum(amt for p, amt, msg in results if p == p2)
    assert p1_wins == 300
    assert p2_wins == 800
    print("Side pot test passed!")

if __name__ == "__main__":
    test_side_pot_basic()
