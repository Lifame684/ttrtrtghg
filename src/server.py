from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
import sys
import os

# Add the current directory to sys.path for Render imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.table import Table
from game.tournament import Tournament
from ai.bot import PokerBot
from game.player import Player
from coach.analyzer import Coach
from game.stats import StatsTracker

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PHASE_TRANSLATION = {
    "preflop": "Префлоп",
    "flop": "Флоп",
    "turn": "Терн",
    "river": "Ривер",
    "showdown": "Вскрытие"
}

class GameStateStore:
    def __init__(self):
        self.table: Optional[Table] = None
        self.tournament: Optional[Tournament] = None
        self.human: Optional[Player] = None
        self.last_analysis: Optional[Dict[str, str]] = None
        self.stats = StatsTracker()
        self.hand_in_pot = False
        self.hand_raised = False
        self.hand_errors = []
        self.starting_stack_of_hand = 0

store = GameStateStore()

class StartGameRequest(BaseModel):
    player_count: int
    starting_stack: int
    scenario: Optional[str] = "classic" # classic, short_stack, bubble, final_table
    difficulty: Optional[str] = "medium" # easy, medium, hard
    avatar_id: Optional[int] = 0

class ActionRequest(BaseModel):
    action: str # fold, call, raise
    amount: Optional[int] = 0

def get_current_state(analysis=None):
    if not store.table or not store.tournament:
        return {"error": "Игра не начата"}
    
    return {
        "pot": store.table.pot,
        "community_cards": [str(c) for c in store.table.community_cards],
        "players": [
            {
                "name": p.name,
                "stack": p.stack,
                "current_bet": p.current_bet,
                "is_active": p.is_active,
                "is_human": p == store.human,
                "avatar_id": getattr(p, 'avatar_id', 0),
                "hand": [str(c) for c in p.hand] if (p == store.human or store.table.phase == "showdown") else ["?", "?"]
            } for p in store.table.players
        ],
        "current_bet": store.table.current_bet,
        "blinds": store.tournament.get_current_blinds(),
        "current_player_idx": store.table.current_player_idx,
        "phase": PHASE_TRANSLATION.get(store.table.phase, store.table.phase),
        "analysis": analysis or store.last_analysis
    }

@app.post("/start")
async def start_game(req: StartGameRequest):
    stack = req.starting_stack
    if req.scenario == "short_stack":
        stack = 300 
    
    avatar_id = req.avatar_id if req.avatar_id is not None else 0
    store.human = Player("ВЫ", stack, avatar_id=avatar_id)
    styles = ["balanced", "maniac", "rock", "shark"]
    
    # Пул доступных аватарок для ботов (исключая выбранную игроком)
    available_avatars = [i for i in range(10) if i != avatar_id]
    random.shuffle(available_avatars)
    
    difficulty = req.difficulty if req.difficulty is not None else "medium"
    
    players_list: List[Player] = [store.human]
    for i in range(req.player_count - 1):
        bot_style = random.choice(styles)
        if req.scenario == "bubble":
            bot_style = "rock"
        
        bot_avatar = available_avatars[i % len(available_avatars)]
        players_list.append(PokerBot(
            f"Бот {i+1}", 
            stack, 
            style=bot_style, 
            difficulty=difficulty,
            avatar_id=bot_avatar
        ))
    
    store.table = Table(players_list)
    store.tournament = Tournament()
    
    if req.scenario == "bubble":
        store.tournament.current_level_idx = 3 
    elif req.scenario == "final_table":
        store.tournament.current_level_idx = 4 
        
    reset_hand_tracking()
    store.table.start_new_hand()
    
    sb, bb = store.tournament.get_current_blinds()
    store.table.players[(store.table.dealer_idx + 1) % len(store.table.players)].bet(sb)
    store.table.players[(store.table.dealer_idx + 2) % len(store.table.players)].bet(bb)
    store.table.current_bet = bb
    
    if store.table.players[store.table.current_player_idx] != store.human:
        process_bots()
    
    return get_current_state()

def reset_hand_tracking():
    if store.human:
        store.starting_stack_of_hand = store.human.stack
    store.hand_in_pot = False
    store.hand_raised = False
    store.hand_errors = []

@app.post("/action")
async def player_action(req: ActionRequest):
    if not store.table or not store.human:
        raise HTTPException(status_code=400, detail="Игра не начата")
    
    current_player = store.table.players[store.table.current_player_idx]
    if current_player != store.human:
        raise HTTPException(status_code=400, detail="Сейчас не ваш ход")

    analysis_grade, analysis_comment = Coach.analyze_preflop(store.human.hand, req.action, "BTN")
    store.last_analysis = {"grade": analysis_grade, "comment": analysis_comment}
    if analysis_grade in ["Ошибка", "Грубая ошибка"]:
        store.hand_errors.append(analysis_grade)

    if req.action == "fold":
        store.human.is_active = False
    elif req.action == "call":
        store.hand_in_pot = True
        amount = store.table.current_bet - store.human.current_bet
        store.human.bet(amount)
    elif req.action == "raise":
        store.hand_in_pot = True
        store.hand_raised = True
        amount = req.amount if req.amount is not None else 0
        store.human.bet(amount)
        store.table.current_bet = store.human.current_bet
        store.table.last_raiser_idx = store.table.current_player_idx

    process_bots()
    
    return get_current_state()

def process_bots():
    if not store.table:
        return
        
    while True:
        if not store.table.next_turn():
            advance_phase()
            break
            
        current_p = store.table.players[store.table.current_player_idx]
        if current_p == store.human:
            break
            
        if isinstance(current_p, PokerBot):
            action, amount = current_p.decide_action(store.table.current_bet, store.table.community_cards, store.table.pot)
            if action == "fold":
                current_p.is_active = False
            elif action == "call":
                current_p.bet(amount)
            elif action == "raise":
                current_p.bet(amount)
                store.table.current_bet = current_p.current_bet
                store.table.last_raiser_idx = store.table.current_player_idx

def advance_phase():
    if not store.table:
        return
        
    store.table.collect_bets()
    if store.table.phase == "preflop":
        store.table.deal_flop()
        store.table.phase = "flop"
    elif store.table.phase == "flop":
        store.table.deal_turn_river()
        store.table.phase = "turn"
    elif store.table.phase == "turn":
        store.table.deal_turn_river()
        store.table.phase = "river"
    elif store.table.phase == "river":
        store.table.phase = "showdown"
        finish_hand()
        return 
    
    store.table.current_player_idx = (store.table.dealer_idx + 1) % len(store.table.players)
    store.table.last_raiser_idx = store.table.dealer_idx
    
    if not store.table.players[store.table.current_player_idx].is_active:
        store.table.next_turn()

def finish_hand():
    if not store.table or not store.human or not store.tournament:
        return
        
    from core.evaluator import Evaluator
    active = store.table.get_active_players()
    best_rank = -1
    winners = []
    
    for p in active:
        rank, _ = Evaluator.evaluate(p.hand + store.table.community_cards)
        if rank > best_rank:
            best_rank = rank
            winners = [p]
        elif rank == best_rank:
            winners.append(p)
    
    win_amount = store.table.pot // len(winners)
    for w in winners:
        w.stack += win_amount
        
    won = store.human in winners
    profit = store.human.stack - store.starting_stack_of_hand
    store.stats.record_hand(store.hand_in_pot, store.hand_raised, won, profit, store.hand_errors)
    
    store.tournament.on_hand_end()
    
    store.table.players = [p for p in store.table.players if p.stack > 0 or p == store.human]
    
    if store.human.stack > 0 and store.tournament:
        reset_hand_tracking()
        store.table.start_new_hand()
        sb, bb = store.tournament.get_current_blinds()
        store.table.players[(store.table.dealer_idx + 1) % len(store.table.players)].bet(sb)
        store.table.players[(store.table.dealer_idx + 2) % len(store.table.players)].bet(bb)
        store.table.current_bet = bb

@app.get("/stats")
async def get_stats():
    return store.stats.get_summary()

@app.get("/state")
async def get_state():
    return get_current_state()

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
