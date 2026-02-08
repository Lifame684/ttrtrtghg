import random
from core.evaluator import HandRank

class Strategy:
    @staticmethod
    def get_action(style, hand_power, needed_to_call, stack, pot_size, phase="preflop", position="BU", board_texture="dry"):
        # Position factors: BU/CO are wide, UTG/MP are tight
        is_late_pos = position in ["BU", "CO", "BTN"]
        is_early_pos = position in ["UTG", "MP"]

        # Board texture factors: "wet" boards (straights/flushes possible) increase aggression or caution

        if style == "nit": # "Нит" - Extremely Tight-Passive
            if hand_power >= HandRank.THREE_OF_A_KIND:
                return ("call", needed_to_call) if needed_to_call < stack * 0.2 else ("fold", 0)
            if hand_power >= HandRank.PAIR and needed_to_call == 0:
                return ("call", 0)
            return ("fold", 0)

        elif style == "maniac": # "Маньяк" - Extremely Loose-Aggressive
            # Bluffs a lot
            if random.random() < 0.4 or hand_power >= HandRank.PAIR:
                return ("raise", needed_to_call + int(pot_size * (0.7 + random.random())))
            return ("call", needed_to_call)

        elif style == "short_stack": # "Шорт-стек" - Push or Fold
            if stack < pot_size * 2:
                if hand_power >= HandRank.PAIR or (is_late_pos and random.random() < 0.3):
                    return ("raise", stack)
                return ("fold", 0)
            # Default to balanced if not really short
            style = "balanced"

        if style == "rock": # "Скала" - Tight-Passive
            if hand_power >= HandRank.THREE_OF_A_KIND:
                if random.random() < 0.3: return ("raise", needed_to_call + int(pot_size * 0.5))
                return ("call", needed_to_call)
            if hand_power >= HandRank.PAIR and needed_to_call < stack * 0.05:
                # Play pairs more cautiously from early pos
                if is_early_pos and needed_to_call > 0: return ("fold", 0)
                return ("call", needed_to_call)
            return ("fold", 0)

        elif style == "calling_station": # "Автоответчик" - Loose-Passive
            if hand_power >= HandRank.FOUR_OF_A_KIND:
                return ("raise", needed_to_call + int(pot_size * 0.3))
            if hand_power >= HandRank.PAIR or needed_to_call < pot_size * 0.6:
                return ("call", needed_to_call)
            return ("fold", 0)

        elif style == "aggressive": # "Агрессивный" - Loose-Aggressive
            # Raise more from late position
            raise_freq = 0.4 if is_late_pos else 0.2
            if hand_power >= HandRank.PAIR or random.random() < raise_freq:
                raise_amt = needed_to_call + int(pot_size * (0.5 + random.random() * 0.5))
                return ("raise", raise_amt)
            if needed_to_call < stack * 0.15:
                return ("call", needed_to_call)
            return ("fold", 0)

        else: # "balanced" - Tight-Aggressive
            # Adjust based on position
            min_power = HandRank.PAIR if is_late_pos else HandRank.THREE_OF_A_KIND
            if hand_power >= HandRank.THREE_OF_A_KIND:
                return ("raise", needed_to_call + int(pot_size * 0.7))
            if hand_power >= HandRank.TWO_PAIR:
                return ("raise", needed_to_call + int(pot_size * 0.4))
            if hand_power >= HandRank.PAIR:
                # Call from late pos, maybe fold from early if bet is large
                if is_early_pos and needed_to_call > pot_size * 0.5: return ("fold", 0)
                return ("call", needed_to_call)
            if needed_to_call == 0: return ("call", 0)

            # Pure bluff in late position
            if is_late_pos and board_texture == "wet" and random.random() < 0.1:
                return ("raise", needed_to_call + int(pot_size * 0.5))

            return ("fold", 0)

        # Fallback
        if hand_power >= HandRank.PAIR: return ("call", needed_to_call)
        return ("fold", 0) if needed_to_call > 0 else ("call", 0)
