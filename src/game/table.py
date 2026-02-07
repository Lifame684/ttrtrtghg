from typing import List
from core.card import Card
from core.deck import Deck
from .player import Player

class Table:
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.dealer_idx = 0
        self.current_bet = 0  # Максимальная ставка в текущем раунде торгов
        self.current_player_idx = 0
        self.phase = "preflop" # preflop, flop, turn, river, showdown
        self.last_raiser_idx = -1

    def start_new_hand(self):
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.phase = "preflop"
        self.last_raiser_idx = -1
        for p in self.players:
            p.reset_hand()
            if p.stack > 0:
                p.hand = self.deck.draw(2)
            else:
                p.is_active = False
        
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        # На префлопе UTG (третий после дилера) ходит первым
        self.current_player_idx = (self.dealer_idx + 3) % len(self.players)
        # На префлопе "последнее слово" у BB, если не было рейзов
        self.last_raiser_idx = (self.dealer_idx + 2) % len(self.players)

    def next_turn(self):
        active = self.get_active_players()
        if len(active) <= 1:
            self.phase = "showdown"
            return False

        # Переходим к следующему
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        
        # Если мы вернулись к тому, кто последний раз повышал (или к BB на префлопе)
        # и этот игрок уже готов ходить, значит круг закончен
        if self.current_player_idx == (self.last_raiser_idx + 1) % len(self.players):
            return False

        # Ищем следующего активного
        iterations = 0
        while iterations < len(self.players):
            p = self.players[self.current_player_idx]
            if p.is_active and not p.is_all_in:
                return True
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            iterations += 1
            if self.current_player_idx == (self.last_raiser_idx + 1) % len(self.players):
                return False
        
        return False

    def deal_flop(self):
        self.community_cards.extend(self.deck.draw(3))

    def deal_turn_river(self):
        self.community_cards.extend(self.deck.draw(1))

    def collect_bets(self):
        for p in self.players:
            self.pot += p.current_bet
            p.current_bet = 0
        self.current_bet = 0

    def get_active_players(self):
        return [p for p in self.players if p.is_active]

    def __repr__(self):
        return f"Table(Pot: {self.pot}, Community: {self.community_cards}, Players: {len(self.players)})"
