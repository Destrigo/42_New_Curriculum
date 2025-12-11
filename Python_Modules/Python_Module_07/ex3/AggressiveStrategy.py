from .GameStrategy import GameStrategy
from typing import List, Dict

class AggressiveStrategy(GameStrategy):
    def get_strategy_name(self) -> str:
        return "AggressiveStrategy"

    def prioritize_targets(self, available_targets: List) -> List:
        # Attack all enemy creatures first, then player
        return sorted(available_targets, key=lambda x: x.get('type', 'player') != 'player')

    def execute_turn(self, hand: List, battlefield: List) -> Dict:
        actions = {"cards_played": [], "mana_used": 0, "targets_attacked": [], "damage_dealt": 0}
        mana_available = 5  # Example fixed mana
        for card in sorted(hand, key=lambda c: getattr(c, "cost", 0)):
            if card.is_playable(mana_available):
                result = card.play({"battlefield": battlefield})
                actions["cards_played"].append(result["card_played"])
                actions["mana_used"] += result["mana_used"]
                if hasattr(card, "attack_target"):
                    actions["targets_attacked"].append("Enemy Player")
                    actions["damage_dealt"] += getattr(card, "attack", 0)
                mana_available -= result["mana_used"]
        return actions
