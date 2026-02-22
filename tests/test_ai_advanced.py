import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from ai.bot import PokerBot
from core.card import Card, Rank, Suit

def test_positional_awareness():
    # Balanced bot
    bot = PokerBot("PosBot", 1000, style="balanced")
    # Give it a marginal hand (Pair of 2s)
    bot.hand = [Card(Rank.TWO, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS)]
    community = [Card(Rank.KING, Suit.DIAMONDS), Card(Rank.TEN, Suit.CLUBS), Card(Rank.SEVEN, Suit.SPADES)]

    # In Early Position, it should be more cautious
    # If there's a bet of 300 (into pot 400), balanced bot should fold from early pos
    action_ep, _ = bot.decide_action(300, community, 400, position="UTG")
    print(f"Balanced EP action with Pair vs 0.75 pot: {action_ep}")
    assert action_ep == "fold"

    # In Late Position, it should call
    action_lp, _ = bot.decide_action(300, community, 400, position="BU")
    print(f"Balanced LP action with Pair vs 0.75 pot: {action_lp}")
    assert action_lp == "call"

    # We expect EP to be fold/call and LP to be call/raise.
    # Actually based on my logic:
    # if is_early_pos and needed_to_call > pot_size * 0.5: return ("fold", 0)
    # here 200 == 400 * 0.5, so it's on the edge.

def test_new_styles():
    # Nit bot
    nit = PokerBot("NitBot", 1000, style="nit")
    nit.hand = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
    community = [Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.TWO, Suit.CLUBS), Card(Rank.THREE, Suit.SPADES)]
    # Has Top Pair. Nit still might fold to a huge bet.
    action, _ = nit.decide_action(800, community, 200) # Calling 800 into 200 pot
    print(f"Nit action with Top Pair vs huge bet: {action}")
    assert action == "fold"

    # Maniac bot
    maniac = PokerBot("ManiacBot", 1000, style="maniac")
    maniac.hand = [Card(Rank.SEVEN, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS)]
    action, _ = maniac.decide_action(100, [], 200)
    print(f"Maniac action with garbage: {action}")
    assert action in ["raise", "call"]

if __name__ == "__main__":
    test_positional_awareness()
    test_new_styles()
