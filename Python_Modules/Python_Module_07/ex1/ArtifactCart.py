from typing import Dict
from ..ex0.Card import Card


class ArtifactCard(Card):
    """Represents a permanent artifact modifier."""
    def __init__(self, name: str, cost: int, rarity: str, durability: int, effect: str):
        super().__init__(name, cost, rarity)
        self.durability = durability
        self.effect = effect

    def activate_ability(self) -> Dict:
        """Demonstrates ongoing passive or activated artifact abilities."""
        return {
            "artifact": self.name,
            "remaining_durability": self.durability,
            "effect": self.effect
        }

    def play(self, game_state: Dict) -> Dict:
        """Playing an artifact puts it in play until destroyed."""
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": self.effect
        }
