import random
from typing import List, Dict
from ..ex0.Card import Card


class Deck:
    """Deck manager capable of storing any card type."""
    def __init__(self) -> None:
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def remove_card(self, card_name: str) -> bool:
        for c in self.cards:
            if c.name == card_name:
                self.cards.remove(c)
                return True
        return False

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw_card(self) -> Card:
        if not self.cards:
            return None
        return self.cards.pop(0)

    def get_deck_stats(self) -> Dict:
        total = len(self.cards)
        creatures = sum(1 for c in self.cards
                        if c.__class__.__name__ == "CreatureCard")
        spells = sum(1 for c in self.cards
                     if c.__class__.__name__ == "SpellCard")
        artifacts = sum(1 for c in self.cards
                        if c.__class__.__name__ == "ArtifactCard")
        avg_cost = sum(c.cost for c
                       in self.cards) / total if total > 0 else 0.0

        return {
            "total_cards": total,
            "creatures": creatures,
            "spells": spells,
            "artifacts": artifacts,
            "avg_cost": avg_cost
        }
