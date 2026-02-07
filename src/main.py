import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from game.player import Player
from game.table import Table
from game.tournament import Tournament
from ai.bot import PokerBot
from core.evaluator import Evaluator
from coach.analyzer import Coach

def run_interactive_session():
    # Создаем 1 игрока и 3 ботов
    human = Player("YOU", 1000)
    bots = [PokerBot(f"Bot_{i}", 1000) for i in range(3)]
    players = [human] + bots
    table = Table(players)
    tournament = Tournament()

    print("\n" + "="*40)
    print("   POKER TOURNAMENT COACH SIMULATOR")
    print("="*40)
    
    while human.stack > 0 and len([p for p in players if p.stack > 0]) > 1:
        table.start_new_hand()
        sb, bb = tournament.get_current_blinds()
        
        print(f"\n[Hand Start] Blinds: {sb}/{bb} | Your Stack: {human.stack}")
        print(f"Your Cards: {human.hand}")
        
        # Ход игрока
        print("\nChoose Action: [f]old, [c]all, [r]aise")
        user_input = "r" # Для демо-режима оставим авто-выбор, но логика готова
        
        action_map = {'f': 'fold', 'c': 'call', 'r': 'raise'}
        action = action_map.get(user_input, 'fold')
        
        # Анализ перед выполнением
        grade, comment = Coach.analyze_preflop(human.hand, action, "BTN")
        print(f"\n>>> COACH VERDICT: {grade.upper()}")
        print(f">>> {comment}")
        
        if action == 'fold':
            human.is_active = False
        else:
            amount = bb * 3 if action == 'raise' else bb
            human.bet(amount)
            table.current_bet = amount

        # Короткий цикл для ботов
        for b in bots:
            b.bet(table.current_bet)
        
        table.collect_bets()
        table.deal_flop()
        print(f"\nFlop: {table.community_cards}")
        
        # Определение победителя
        active = table.get_active_players()
        best_rank = -1
        winner = None
        for p in active:
            rank, _ = Evaluator.evaluate(p.hand + table.community_cards)
            if rank > best_rank:
                best_rank = rank
                winner = p
        
        print(f"WINNER: {winner.name} (Rank: {best_rank})")
        
        if tournament.on_hand_end():
            print("\n!!! BLINDS INCREASED !!!")
            
        break # Выходим после одной раздачи для демонстрации

if __name__ == "__main__":
    run_interactive_session()
