from typing import Dict, List
from ex0.Card import Card


class SpellCard(Card):
    """Represents a one-time spell effect (damage, heal, buff, debuff)."""

    def __init__(self, name: str, cost: int, rarity: str, effect_type: str):
        super().__init__(name, cost, rarity)
        self.effect_type = effect_type

    def resolve_effect(self, targets: List) -> Dict:
        """Resolves spell mechanics. This i
          a fake implementation for demonstration."""
        return {
            "spell": self.name,
            "effect_type": self.effect_type,
            "targets": [t.name for t in targets] if targets else []
        }

    def play(self, game_state: Dict) -> Dict:
        """Playing a spell consumes it. One-time effect."""
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": ("Deal 3 damage to "
                       "target" if self.effect_type == "damage"
                       "" else f"Effect: {self.effect_type}")
        }
