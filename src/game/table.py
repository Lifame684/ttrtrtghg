from typing import List, Optional, Tuple
from core.card import Card
from core.deck import Deck
from core.evaluator import Evaluator
from .player import Player

class Table:
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.dealer_idx = 0
        self.current_bet = 0
        self.min_raise = 0
        self.current_player_idx = 0
        self.phase = "preflop"
        self.last_raiser_idx = -1
        self.players_acted = set()

    def start_new_hand(self, small_blind: int, big_blind: int, tournament: Optional['Tournament'] = None):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = big_blind
        self.min_raise = big_blind
        self.phase = "preflop"
        self.players_acted = set()

        bb_idx = (self.dealer_idx + 2) % len(self.players)
        active_count = len([p for p in self.players if p.stack > 0])
        if active_count == 2:
            bb_idx = (self.dealer_idx + 1) % len(self.players)

        for i, p in enumerate(self.players):
            p.reset_hand()
            if p.stack > 0:
                p.hand = self.deck.draw(2)
                ante_to_pay = 0
                if tournament:
                    ante_to_pay = tournament.get_ante_to_pay(i == bb_idx)
                p.bet(ante_to_pay)
            else:
                p.is_active = False

        active_count = len([p for p in self.players if p.is_active])
        if active_count < 2: return

        sb_idx = (self.dealer_idx + 1) % len(self.players)
        bb_idx = (self.dealer_idx + 2) % len(self.players)
        if active_count == 2:
            sb_idx = self.dealer_idx
            bb_idx = (self.dealer_idx + 1) % len(self.players)

        # Ensure active players for blinds
        while not self.players[sb_idx].is_active: sb_idx = (sb_idx + 1) % len(self.players)
        bb_idx = (sb_idx + 1) % len(self.players)
        while not self.players[bb_idx].is_active: bb_idx = (bb_idx + 1) % len(self.players)

        self.players[sb_idx].bet(small_blind)
        self.players[bb_idx].bet(big_blind)
        
        self.last_raiser_idx = bb_idx
        self.current_player_idx = (bb_idx + 1) % len(self.players)
        self._ensure_valid_player()

    def _ensure_valid_player(self):
        iterations = 0
        while iterations < len(self.players):
            p = self.players[self.current_player_idx]
            if p.is_active and not p.is_all_in: return
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            iterations += 1

    def handle_action(self, player: Player, action: str, amount: int = 0):
        if action == "fold":
            player.is_active = False
        elif action == "call":
            call_amount = self.current_bet - player.current_bet
            player.bet(call_amount)
        elif action == "raise":
            if amount < self.current_bet + self.min_raise:
                amount = self.current_bet + self.min_raise
            player.bet(amount - player.current_bet)
            if player.current_bet > self.current_bet:
                self.min_raise = player.current_bet - self.current_bet
                self.current_bet = player.current_bet
                self.last_raiser_idx = self.players.index(player)
        self.players_acted.add(self.players.index(player))

    def is_betting_round_over(self) -> bool:
        active_players = [p for p in self.players if p.is_active and not p.is_all_in]
        if len(active_players) <= 1:
            if len(active_players) == 1:
                p = active_players[0]
                if p.current_bet < self.current_bet and self.players.index(p) not in self.players_acted:
                    return False
            return True
        for p in active_players:
            if self.players.index(p) not in self.players_acted or p.current_bet < self.current_bet:
                return False
        return True

    def next_phase(self):
        self.collect_bets()
        self.players_acted = set()
        self.current_bet = 0
        self.min_raise = 0
        if self.phase == "preflop": self.deal_flop(); self.phase = "flop"
        elif self.phase == "flop": self.deal_turn_river(); self.phase = "turn"
        elif self.phase == "turn": self.deal_turn_river(); self.phase = "river"
        elif self.phase == "river": self.phase = "showdown"

        if self.phase != "showdown":
            self.current_player_idx = (self.dealer_idx + 1) % len(self.players)
            self._ensure_valid_player()
            self.last_raiser_idx = -1
            if not any(p.is_active and not p.is_all_in for p in self.players):
                while self.phase != "showdown":
                    if self.phase == "flop": self.deal_turn_river(); self.phase = "turn"
                    elif self.phase == "turn": self.deal_turn_river(); self.phase = "river"
                    elif self.phase == "river": self.phase = "showdown"

    def deal_flop(self): self.community_cards.extend(self.deck.draw(3))
    def deal_turn_river(self): self.community_cards.extend(self.deck.draw(1))

    def collect_bets(self):
        for p in self.players:
            self.pot += p.current_bet
            p.current_bet = 0
        self.current_bet = 0

    def resolve_winners(self) -> List[Tuple[Player, int, str]]:
        results = []
        contributing_players = [p for p in self.players if p.total_contribution > 0]
        while contributing_players:
            contributing_players.sort(key=lambda x: x.total_contribution)
            smallest = contributing_players[0].total_contribution
            pot_amount = 0
            eligible = []
            for p in contributing_players:
                pot_amount += smallest
                p.total_contribution -= smallest
                if p.is_active: eligible.append(p)
            if eligible:
                best_rank = -1
                winners = []
                for p in eligible:
                    rank, kickers = Evaluator.evaluate(p.hand + self.community_cards)
                    if rank > best_rank:
                        best_rank, best_kickers, winners = rank, kickers, [p]
                    elif rank == best_rank:
                        if kickers > best_kickers:
                            best_kickers, winners = kickers, [p]
                        elif kickers == best_kickers:
                            winners.append(p)
                win_per = pot_amount // len(winners)
                for w in winners:
                    w.stack += win_per
                    results.append((w, win_per, "Won side pot"))
                winners[0].stack += pot_amount % len(winners)
            contributing_players = [p for p in contributing_players if p.total_contribution > 0]
        return results

    def get_active_players(self): return [p for p in self.players if p.is_active]
    def __repr__(self): return f"Table(Phase: {self.phase}, Pot: {self.pot})"
