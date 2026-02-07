import random
from core.evaluator import HandRank

class Strategy:
    @staticmethod
    def get_action(style, hand_power, needed_to_call, stack, pot_size):
        if style == "maniac":
            # Loose-Aggressive
            if hand_power >= HandRank.PAIR or random.random() < 0.3:
                return ("raise", needed_to_call + int(pot_size * 0.75))
            return ("call", needed_to_call)

        elif style == "rock":
            # Tight-Passive
            if hand_power >= HandRank.THREE_OF_A_KIND:
                return ("call", needed_to_call)
            if hand_power >= HandRank.PAIR and needed_to_call < stack * 0.05:
                return ("call", needed_to_call)
            return ("fold", 0)

        elif style == "shark":
            # Tight-Aggressive
            if hand_power >= HandRank.THREE_OF_A_KIND:
                return ("raise", needed_to_call + int(pot_size * 0.5))
            if hand_power >= HandRank.PAIR:
                return ("call", needed_to_call)
            return ("fold", 0)

        else: # Balanced / GTO-lite
            if hand_power >= HandRank.TWO_PAIR:
                return ("raise", needed_to_call + int(pot_size * 0.4))
            if hand_power >= HandRank.PAIR or needed_to_call < stack * 0.1:
                return ("call", needed_to_call)
            return ("fold", 0)
