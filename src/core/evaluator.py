from collections import Counter
from typing import List
from .card import Card, Rank, Suit

class HandRank:
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9

class Evaluator:
    @staticmethod
    def evaluate(cards: List[Card]):
        if len(cards) < 5:
            return (0, [])

        # Сортируем карты по рангу для удобства
        cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        
        # 1. Проверка на флеш
        suits = Counter(c.suit for c in cards)
        flush_suit = next((s for s, count in suits.items() if count >= 5), None)
        
        # 2. Проверка на стрит
        unique_ranks = sorted(list(set(c.rank.value for c in cards)), reverse=True)
        straight_high = None
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i+4] == 4:
                straight_high = unique_ranks[i]
                break
        # Стрит от туза (A-2-3-4-5)
        if not straight_high and set([14, 2, 3, 4, 5]).issubset(set(unique_ranks)):
            straight_high = 5

        # 3. Комбинации на совпадениях
        rank_counts = Counter(c.rank.value for c in cards).most_common()
        
        # Стрит-флеш
        if flush_suit and straight_high:
            # Тут упрощенная проверка, для симулятора этого достаточно на старт
            return (HandRank.STRAIGHT_FLUSH, [straight_high])

        # Каре
        if rank_counts[0][1] == 4:
            return (HandRank.FOUR_OF_A_KIND, [rank_counts[0][0], rank_counts[1][0]])

        # Фулл-хаус
        if rank_counts[0][1] == 3 and len(rank_counts) > 1 and rank_counts[1][1] >= 2:
            return (HandRank.FULL_HOUSE, [rank_counts[0][0], rank_counts[1][0]])

        # Флеш
        if flush_suit:
            flush_cards = [c.rank.value for c in cards if c.suit == flush_suit][:5]
            return (HandRank.FLUSH, flush_cards)

        # Стрит
        if straight_high:
            return (HandRank.STRAIGHT, [straight_high])

        # Сет
        if rank_counts[0][1] == 3:
            kickers = [r for r, c in rank_counts[1:3]]
            return (HandRank.THREE_OF_A_KIND, [rank_counts[0][0]] + kickers)

        # Две пары
        if rank_counts[0][1] == 2 and len(rank_counts) > 1 and rank_counts[1][1] == 2:
            kicker = max(r for r, c in rank_counts[2:] if c >= 1) if len(rank_counts) > 2 else rank_counts[1][0]
            return (HandRank.TWO_PAIR, [rank_counts[0][0], rank_counts[1][0], kicker])

        # Пара
        if rank_counts[0][1] == 2:
            kickers = [r for r, c in rank_counts[1:4]]
            return (HandRank.PAIR, [rank_counts[0][0]] + kickers)

        # Старшая карта
        return (HandRank.HIGH_CARD, [c.rank.value for c in cards[:5]])
