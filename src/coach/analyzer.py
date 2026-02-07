from core.card import Rank
from core.evaluator import Evaluator, HandRank

class ActionGrade:
    GREAT = "Отличный ход"
    GOOD = "Хорошо"
    INACCURACY = "Неточность"
    MISTAKE = "Ошибка"
    BLUNDER = "Грубая ошибка"

class Coach:
    @staticmethod
    def analyze_preflop(hand, action, position):
        # Очень упрощенная GTO логика для примера:
        ranks = sorted([hand[0].rank.value, hand[1].rank.value], reverse=True)
        is_pair = ranks[0] == ranks[1]
        
        # Топ руки
        premium = is_pair and ranks[0] >= 10 # TT+
        strong = (ranks[0] == 14 and ranks[1] >= 12) or premium # AK, AQ, TT+

        if action == "fold" and strong:
            return ActionGrade.BLUNDER, "Вы сбросили премиум-руку на префлопе!"
        
        if action == "raise" and ranks[0] < 7 and not is_pair:
            return ActionGrade.MISTAKE, "Рейз с очень слабой рукой слишком рискован."
            
        return ActionGrade.GREAT, "Хорошее решение."

    @staticmethod
    def analyze_pot_odds(win_probability, call_amount, pot_size):
        # Шансы банка: сколько нужно доставить / (сколько в банке + сколько доставляем)
        if call_amount == 0:
            return ActionGrade.GREAT, "Чек/колл при нулевой ставке оправдан."
            
        pot_odds = call_amount / (pot_size + call_amount)
        if win_probability < pot_odds:
            return ActionGrade.MISTAKE, f"Математически невыгодно. Нужно {pot_odds:.2%} эквити, а у вас только {win_probability:.2%}"
        return ActionGrade.GREAT, "Математически обоснованный колл."
