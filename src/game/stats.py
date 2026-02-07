import json
import os
from datetime import datetime

STATS_FILE = "poker_stats.json"

class StatsTracker:
    def __init__(self):
        self.stats = self._load_stats()

    def _load_stats(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "total_hands": 0,
            "vpip_hands": 0,
            "pfr_hands": 0,
            "wins": 0,
            "total_profit": 0,
            "mistakes": 0,
            "blunders": 0,
            "sessions": []
        }

    def save(self):
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=4)

    def record_hand(self, entered_pot, raised, won, profit, errors):
        self.stats["total_hands"] += 1
        if entered_pot:
            self.stats["vpip_hands"] += 1
        if raised:
            self.stats["pfr_hands"] += 1
        if won:
            self.stats["wins"] += 1
        
        self.stats["total_profit"] += profit
        
        for err in errors:
            if err == "Ошибка":
                self.stats["mistakes"] += 1
            elif err == "Грубая ошибка":
                self.stats["blunders"] += 1
        
        self.save()

    def get_summary(self):
        total = max(1, self.stats["total_hands"])
        return {
            "vpip": round((self.stats["vpip_hands"] / total) * 100, 1),
            "pfr": round((self.stats["pfr_hands"] / total) * 100, 1),
            "win_rate": round((self.stats["wins"] / total) * 100, 1),
            "profit": self.stats["total_profit"],
            "total_hands": self.stats["total_hands"],
            "errors": self.stats["mistakes"] + self.stats["blunders"]
        }
