from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from game.table import Table
from game.tournament import Tournament
from ai.bot import PokerBot
from game.player import Player
from coach.analyzer import Coach
from game.stats import StatsTracker

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PHASE_TRANSLATION = {"preflop": "Префлоп", "flop": "Флоп", "turn": "Терн", "river": "Ривер", "showdown": "Вскрытие"}

class GameStateStore:
    def __init__(self):
        self.table: Optional[Table] = None
        self.tournament: Optional[Tournament] = None
        self.human: Optional[Player] = None
        self.last_analysis: Optional[Dict[str, str]] = None
        self.stats = StatsTracker()
        self.hand_in_pot, self.hand_raised, self.hand_errors, self.hand_error_comments = False, False, [], []
        self.starting_stack_of_hand = 0

store = GameStateStore()

class StartGameRequest(BaseModel):
    player_count: int; starting_stack: int; scenario: Optional[str] = "classic"; difficulty: Optional[str] = "medium"; avatar_id: Optional[int] = 0
class ActionRequest(BaseModel):
    action: str; amount: Optional[int] = 0

def get_current_state(analysis=None):
    if not store.table or not store.tournament: return {"error": "Игра не начата"}
    sb, bb, ante = store.tournament.get_current_level()
    players_data = []
    for i, p in enumerate(store.table.players):
        pos = "MP"; d_idx = store.table.dealer_idx; p_count = len(store.table.players)
        if i == d_idx: pos = "BTN"
        elif i == (d_idx + 1) % p_count: pos = "SB"
        elif i == (d_idx + 2) % p_count: pos = "BB"
        elif i == (d_idx + 3) % p_count: pos = "UTG"
        players_data.append({
            "name": p.name, "stack": p.stack, "current_bet": p.current_bet, "is_active": p.is_active,
            "is_human": p == store.human, "position": pos, "avatar_id": getattr(p, 'avatar_id', 0),
            "hand": [str(c) for c in p.hand] if (p == store.human or store.table.phase == "showdown") else ["?", "?"]
        })
    return {
        "pot": store.table.pot, "community_cards": [str(c) for c in store.table.community_cards],
        "players": players_data, "current_bet": store.table.current_bet, "blinds": [sb, bb], "ante": ante,
        "current_player_idx": store.table.current_player_idx, "phase": PHASE_TRANSLATION.get(store.table.phase, store.table.phase),
        "analysis": analysis or store.last_analysis
    }

@app.post("/start")
async def start_game(req: StartGameRequest):
    stack = req.starting_stack
    if req.scenario == "short_stack": stack = 300
    store.human = Player("ВЫ", stack, avatar_id=req.avatar_id)
    styles = ["balanced", "aggressive", "rock", "calling_station", "nit", "maniac"]
    available_avatars = [i for i in range(10) if i != req.avatar_id]
    random.shuffle(available_avatars)
    players_list = [store.human]
    for i in range(req.player_count - 1):
        players_list.append(PokerBot(f"Бот {i+1}", stack, style=random.choice(styles), difficulty=req.difficulty, avatar_id=available_avatars[i % len(available_avatars)]))
    store.table = Table(players_list)
    store.tournament = Tournament(ante_type="bb_ante" if req.scenario in ["bubble", "final_table"] else "none")
    if req.scenario == "bubble": store.tournament.current_level_idx = 3
    elif req.scenario == "final_table": store.tournament.current_level_idx = 4
    reset_hand_tracking()
    sb, bb, ante = store.tournament.get_current_level()
    store.table.start_new_hand(sb, bb, store.tournament)
    if store.table.players[store.table.current_player_idx] != store.human: process_bots()
    return get_current_state()

def reset_hand_tracking():
    if store.human: store.starting_stack_of_hand = store.human.stack
    store.hand_in_pot, store.hand_raised, store.hand_errors, store.hand_error_comments = False, False, [], []

@app.post("/action")
async def player_action(req: ActionRequest):
    if not store.table or not store.human: raise HTTPException(status_code=400, detail="Игра не начата")
    current_player = store.table.players[store.table.current_player_idx]
    if current_player != store.human: raise HTTPException(status_code=400, detail="Сейчас не ваш ход")
    human_idx = store.table.players.index(store.human); d_idx = store.table.dealer_idx; p_count = len(store.table.players); pos = "MP"
    if human_idx == d_idx: pos = "BTN"
    elif human_idx == (d_idx + 1) % p_count: pos = "SB"
    elif human_idx == (d_idx + 2) % p_count: pos = "BB"
    if store.table.phase == "preflop":
        _, bb, _ = store.tournament.get_current_level()
        grade, comment, recommended = Coach.analyze_preflop(store.human.hand, req.action, pos, int(store.human.stack / bb), store.table.current_bet / bb)
    else:
        call_amount = store.table.current_bet - store.human.current_bet
        grade, comment, recommended = Coach.analyze_postflop(store.human.hand, store.table.community_cards, req.action, call_amount, store.table.pot)
    store.last_analysis = {"grade": grade, "comment": comment, "recommended": recommended}
    print(f"Analysis: {store.last_analysis}")
    if grade in ["Ошибка", "Грубая ошибка"]: store.hand_errors.append(grade); store.hand_error_comments.append(comment)
    store.table.handle_action(store.human, req.action, req.amount)
    if req.action != "fold":
        store.hand_in_pot = True
        if req.action == "raise": store.hand_raised = True
    process_bots()
    return get_current_state()

def process_bots():
    if not store.table: return
    while True:
        if store.table.is_betting_round_over(): advance_phase(); break
        current_p = store.table.players[store.table.current_player_idx]
        if current_p == store.human: break
        if isinstance(current_p, PokerBot):
            stage = "early"
            if store.tournament.current_level_idx >= 3: stage = "bubble"
            if len(store.table.players) <= 3: stage = "final_table"
            # Calc position
            idx = store.table.players.index(current_p); d = store.table.dealer_idx; cnt = len(store.table.players); p_str = "MP"
            if idx == d: p_str = "BTN"
            elif idx == (d+1)%cnt: p_str = "SB"
            elif idx == (d+2)%cnt: p_str = "BB"
            elif idx == (d+3)%cnt: p_str = "UTG"
            action, amount = current_p.decide_action(store.table.current_bet, store.table.community_cards, store.table.pot, stage, position=p_str)
            store.table.handle_action(current_p, action, amount)
        store.table.current_player_idx = (store.table.current_player_idx + 1) % len(store.table.players)
        found = False
        for _ in range(len(store.table.players)):
            p = store.table.players[store.table.current_player_idx]
            if p.is_active and not p.is_all_in: found = True; break
            store.table.current_player_idx = (store.table.current_player_idx + 1) % len(store.table.players)
        if not found: break

def advance_phase():
    if not store.table: return
    store.table.next_phase()
    if store.table.phase == "showdown": finish_hand()

def finish_hand():
    if not store.table or not store.human or not store.tournament: return
    results = store.table.resolve_winners()
    won = any(r[0] == store.human for r in results)
    profit = store.human.stack - store.starting_stack_of_hand
    store.stats.record_hand(store.hand_in_pot, store.hand_raised, won, profit, store.human.stack, store.hand_errors, store.hand_error_comments)
    store.tournament.on_hand_end(store.table.players)
    store.table.players = [p for p in store.table.players if p.stack > 0 or p == store.human]
    if store.human.stack > 0 and len(store.table.players) > 1:
        reset_hand_tracking(); dealer_idx = (store.table.dealer_idx + 1) % len(store.table.players)
        table_players = store.table.players; store.table = Table(table_players); store.table.dealer_idx = dealer_idx
        sb, bb, ante = store.tournament.get_current_level(); store.table.start_new_hand(sb, bb, store.tournament)
        if store.table.players[store.table.current_player_idx] != store.human: process_bots()

@app.get("/stats")
async def get_stats(): return store.stats.get_summary()
@app.get("/state")
async def get_state(): return get_current_state()

if __name__ == "__main__":
    import uvicorn; import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
