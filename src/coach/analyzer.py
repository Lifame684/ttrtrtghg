from core.card import Rank, Card
from core.evaluator import Evaluator, HandRank
from typing import List, Tuple

class ActionGrade:
    GREAT = "Отличный ход"
    GOOD = "Хорошо"
    INACCURACY = "Неточность"
    MISTAKE = "Ошибка"
    BLUNDER = "Грубая ошибка"

class Coach:
    @staticmethod
    def analyze_preflop(hand: List[Card], action: str, position: str, stack_bb: int, current_bet_bb: float) -> Tuple[str, str, str]:
        ranks = sorted([hand[0].rank.value, hand[1].rank.value], reverse=True)
        is_pair = ranks[0] == ranks[1]
        is_suited = hand[0].suit == hand[1].suit
        premium = (is_pair and ranks[0] >= 11) or (ranks[0] == 14 and ranks[1] == 13 and is_suited)
        strong = premium or (is_pair and ranks[0] >= 9) or (ranks[0] == 14 and ranks[1] >= 11) or (ranks[0] == 13 and ranks[1] >= 12 and is_suited)
        playable = strong or is_pair or (is_suited and ranks[0] - ranks[1] == 1) or (ranks[0] >= 12 and ranks[1] >= 10)

        recommended = "fold"
        if premium or strong: recommended = "raise"
        elif playable and position in ["BU", "CO", "BTN"]: recommended = "call"
        if current_bet_bb > 2:
            if not strong: recommended = "fold"
            else: recommended = "raise"

        verdict, comment = ActionGrade.GOOD, "Приемлемое решение."
        if action == "fold":
            if premium: verdict, comment = ActionGrade.BLUNDER, "Никогда не сбрасывайте премиум-руки на префлопе!"
            elif strong: verdict, comment = ActionGrade.MISTAKE, f"Эта рука ({ranks[0]}{ranks[1]}) слишком сильна для фолда."
            else: verdict, comment = ActionGrade.GREAT, "Правильный фолд."
        elif action == "raise":
            if not playable and current_bet_bb <= 2: verdict, comment = ActionGrade.MISTAKE, "Рейз с такой слабой рукой — это неоправданный блеф."
            elif current_bet_bb > 5 and not strong: verdict, comment = ActionGrade.BLUNDER, "4-бет с посредственной рукой слишком рискован."
            else: verdict, comment = ActionGrade.GREAT, "Хороший рейз."
        elif action == "call":
            if premium: verdict, comment = ActionGrade.INACCURACY, "С такими картами нужно играть агрессивнее (3-бет)."
            elif not playable and current_bet_bb > 2: verdict, comment = ActionGrade.MISTAKE, "Колл рейза со слабой рукой — ошибка."
            else: verdict, comment = ActionGrade.GOOD, "Колл допустим."

        return verdict, comment, recommended

    @staticmethod
    def calculate_equity_simple(hand: List[Card], community: List[Card]) -> float:
        rank, _ = Evaluator.evaluate(hand + community)
        if not community: return 0.5
        rank_equity = {
            HandRank.STRAIGHT_FLUSH: 0.99, HandRank.FOUR_OF_A_KIND: 0.98,
            HandRank.FULL_HOUSE: 0.95, HandRank.FLUSH: 0.90,
            HandRank.STRAIGHT: 0.85, HandRank.THREE_OF_A_KIND: 0.75,
            HandRank.TWO_PAIR: 0.60, HandRank.PAIR: 0.35,
            HandRank.HIGH_CARD: 0.15
        }
        return rank_equity.get(rank, 0.1)

    @staticmethod
    def analyze_postflop(hand: List[Card], community: List[Card], action: str, call_amount: int, pot_size: int) -> Tuple[str, str, str]:
        equity = Coach.calculate_equity_simple(hand, community)
        pot_odds = call_amount / (pot_size + call_amount) if call_amount > 0 else 0
        recommended = "check"
        if equity > 0.7: recommended = "raise"
        elif equity > 0.3: recommended = "call"
        else: recommended = "fold"
        if action == "fold":
            if equity > 0.4 and pot_odds < 0.2: return ActionGrade.MISTAKE, f"Вы выбросили сильную руку ({equity:.0%}).", recommended
            return ActionGrade.GREAT, "Хороший фолд.", recommended
        if action in ["call", "raise"]:
            if call_amount == 0:
                if equity > 0.8: return ActionGrade.INACCURACY, "У вас монстр-рука! Ставьте сами.", "raise"
                return ActionGrade.GREAT, "Правильный чек.", recommended
            if equity < pot_odds - 0.05: return ActionGrade.MISTAKE, f"Невыгодный колл. Нужно {pot_odds:.1%}, а у вас {equity:.1%}.", recommended
            return ActionGrade.GREAT, "Математически обоснованный колл.", recommended
        return ActionGrade.GOOD, "Ход принят.", recommended
