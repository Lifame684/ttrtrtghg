from collections import Counter
from typing import List, Tuple
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
    def evaluate(cards: List[Card]) -> Tuple[int, List[int]]:
        if len(cards) < 5:
            return (0, [])

        cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        
        suits = Counter(c.suit for c in cards)
        flush_suit = next((s for s, count in suits.items() if count >= 5), None)
        
        if flush_suit:
            flush_cards = [c for c in cards if c.suit == flush_suit]
            flush_ranks = sorted(list(set(c.rank.value for c in flush_cards)), reverse=True)
            straight_flush_high = Evaluator._get_straight_high(flush_ranks)
            if straight_flush_high:
                return (HandRank.STRAIGHT_FLUSH, [straight_flush_high])

        rank_counts = Counter(c.rank.value for c in cards).most_common()
        if rank_counts[0][1] == 4:
            quad_rank = rank_counts[0][0]
            kicker = max(r for r, c in rank_counts if r != quad_rank)
            return (HandRank.FOUR_OF_A_KIND, [quad_rank, kicker])

        if rank_counts[0][1] == 3:
            trips_rank = rank_counts[0][0]
            pair_rank = next((r for r, c in rank_counts if r != trips_rank and c >= 2), None)
            if pair_rank:
                return (HandRank.FULL_HOUSE, [trips_rank, pair_rank])

        if flush_suit:
            flush_ranks = [c.rank.value for c in cards if c.suit == flush_suit][:5]
            return (HandRank.FLUSH, flush_ranks)

        unique_ranks = sorted(list(set(c.rank.value for c in cards)), reverse=True)
        straight_high = Evaluator._get_straight_high(unique_ranks)
        if straight_high:
            return (HandRank.STRAIGHT, [straight_high])

        if rank_counts[0][1] == 3:
            trips_rank = rank_counts[0][0]
            kickers = sorted([r for r, c in rank_counts if r != trips_rank], reverse=True)[:2]
            return (HandRank.THREE_OF_A_KIND, [trips_rank] + kickers)

        if rank_counts[0][1] == 2 and len(rank_counts) > 1 and rank_counts[1][1] == 2:
            pairs = sorted([rank_counts[0][0], rank_counts[1][0]], reverse=True)
            if len(rank_counts) > 2 and rank_counts[2][1] == 2:
                pairs = sorted([rank_counts[0][0], rank_counts[1][0], rank_counts[2][0]], reverse=True)[:2]
            kicker = max(r for r, c in rank_counts if r not in pairs)
            return (HandRank.TWO_PAIR, pairs + [kicker])

        if rank_counts[0][1] == 2:
            pair_rank = rank_counts[0][0]
            kickers = sorted([r for r, c in rank_counts if r != pair_rank], reverse=True)[:3]
            return (HandRank.PAIR, [pair_rank] + kickers)

        return (HandRank.HIGH_CARD, [c.rank.value for c in cards[:5]])

    @staticmethod
    def _get_straight_high(ranks: List[int]) -> int:
        for i in range(len(ranks) - 4):
            if ranks[i] - ranks[i+4] == 4:
                return ranks[i]
        if set([14, 2, 3, 4, 5]).issubset(set(ranks)):
            return 5
        return None
