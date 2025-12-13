from ex0.Card import Card
from ex2.Combatable import Combatable
from .Rankable import Rankable
from typing import Dict


class TournamentCard(Card, Combatable, Rankable):
    def __init__(self, name: str,
                 cost: int, rarity: str,
                 att: int, health: int) -> None:
        super().__init__(name, cost, rarity)
        self.att = att
        self.health = health
        self.wins = 0
        self.losses = 0
        self.rating = 1200  # Default starting rating

    def play(self, game_state: Dict) -> Dict:
        return {"card_played": self.name, "mana_used": self.cost,
                "effect": "Creature summoned to battlefield"}

    def attack(self, target) -> Dict:
        damage = self.attack
        return {"attacker": self.name,
                "target": getattr(target, "name", str(target)),
                "damage": damage, "combat_resolved": True}

    def defend(self, incoming_damage: int) -> Dict:
        blocked = min(self.health, incoming_damage // 2)
        self.health -= incoming_damage - blocked
        still_alive = self.health > 0
        return {"defender": self.name,
                "damage_taken": incoming_damage,
                "damage_blocked": blocked,
                "still_alive": still_alive}

    def get_combat_stats(self) -> Dict:
        return {"att": self.att, "health": self.health}

    # Rankable interface
    def calculate_rating(self) -> int:
        # Simple Elo-like adjustment
        return self.rating

    def update_wins(self, wins: int) -> None:
        self.wins += wins
        self.rating += 16 * wins

    def update_losses(self, losses: int) -> None:
        self.losses += losses
        self.rating -= 16 * losses

    def get_rank_info(self) -> Dict:
        return {"rating": self.rating, "record": f"{self.wins}-{self.losses}"}

    # Tournament stats
    def get_tournament_stats(self) -> Dict:
        return {"name": self.name,
                "rating": self.rating,
                "wins": self.wins,
                "losses": self.losses}
