from typing import Dict, List
from ex0.Card import Card
from .Combatable import Combatable
from .Magical import Magical


class EliteCard(Card, Combatable, Magical):
    """
    A powerful card that combines combat and magical interfaces.
    Implements all abstract methods from Card, Combatable, and Magical.
    """

    def __init__(
        self,
        name: str,
        cost: int,
        rarity: str,
        att: int,
        health: int,
        base_mana: int = 0,
    ):
        super().__init__(name, cost, rarity)

        if att <= 0 or health <= 0:
            raise ValueError("Attack and health must be positive integers.")

        self.att = att
        self.health = health
        self.mana = base_mana

    # Card abstract implementation
    def play(self, game_state: Dict) -> Dict:
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": "Elite unit summoned with combat and magic capabilities",
        }

    # Combatable implementations
    def attack(self, target) -> Dict:
        return {
            "attacker": self.name,
            "target": getattr(target, "name", str(target)),
            "damage": self.att,
            "combat_type": "melee",
        }

    def defend(self, incoming_damage: int) -> Dict:
        """
        Very simple defense: block up to half of incoming damage (rounded down)
        Remaining damage reduces health.
        """
        damage_blocked = incoming_damage // 2
        damage_taken = incoming_damage - damage_blocked
        self.health -= damage_taken
        still_alive = self.health > 0
        return {
            "defender": self.name,
            "damage_taken": damage_taken,
            "damage_blocked": damage_blocked,
            "still_alive": still_alive,
        }

    def get_combat_stats(self) -> Dict:
        return {"att": self.att, "health": self.health}

    def cast_spell(self, spell_name: str, targets: List) -> Dict:
        mana_cost = 4 if spell_name.lower() == "fireball" else 2
        if self.mana < mana_cost:
            return {
                "caster": self.name,
                "spell": spell_name,
                "targets": [getattr(t, "name", str(t)) for t in targets],
                "mana_used": 0,
                "result": "failed - insufficient mana",
            }

        self.mana -= mana_cost
        return {
            "caster": self.name,
            "spell": spell_name,
            "targets": [getattr(t, "name", str(t)) for t in targets],
            "mana_used": mana_cost,
        }

    def channel_mana(self, amount: int) -> Dict:
        """
        Increase mana pool and return the updated state.
        """
        if amount < 0:
            raise ValueError("Cannot channel a negative amount of mana.")
        self.mana += amount
        return {"channeled": amount, "total_mana": self.mana}

    def get_magic_stats(self) -> Dict:
        return {"mana": self.mana}
