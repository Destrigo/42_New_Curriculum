from Card import Card


class CreatureCard(Card):
    def __init__(
                self, name: str, cost: int,
                rarity: str, attack: int, health: int) -> None:
        super().__init__(name, cost, rarity)
        if attack < 0:
            print("Error! Creatures can't have negative attack value")
        else:
            self.attack = attack
        if health < 0:
            print("Error! Creatures can't have negative health value")
        else:
            self.health = health

    def play(self, game_state: dict) -> dict:
        """can do stuff"""
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": "Creature summoned to battlefield"
        }

    def attack_target(self, target) -> dict:
        """attacking"""
        return {
            "attacker": self.name,
            "target": target.name,
            "damage_dealt": self.attack,
            "combat_resolved": True
        }
