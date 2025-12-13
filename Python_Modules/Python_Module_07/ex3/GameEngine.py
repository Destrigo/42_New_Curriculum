from .CardFactory import CardFactory
from .GameStrategy import GameStrategy
from typing import Dict


class GameEngine:
    def __init__(self):
        self.factory: CardFactory = None
        self.strategy: GameStrategy = None
        self.hand = []
        self.battlefield = []
        self.turns_simulated = 0
        self.actions_log = []

    def configure_engine(self,
                         factory: CardFactory,
                         strategy: GameStrategy) -> None:
        self.factory = factory
        self.strategy = strategy
        self.hand = [factory.create_creature("Fire Dragon"),
                     factory.create_creature("Goblin Warrior"),
                     factory.create_spell("Lightning Bolt")]
        self.battlefield = []

    def simulate_turn(self) -> Dict:
        if not self.factory or not self.strategy:
            raise Exception("Engine not configured")
        self.turns_simulated += 1
        actions = self.strategy.execute_turn(self.hand, self.battlefield)
        self.actions_log.append(actions)
        return {
            "turns_simulated": self.turns_simulated,
            "strategy_used": self.strategy.get_strategy_name(),
            "total_damage": actions.get("damage_dealt", 0),
            "cards_created": len(self.hand)
        }

    def get_engine_status(self) -> Dict:
        return {
            "hand_size": len(self.hand),
            "battlefield_size": len(self.battlefield),
            "turns_simulated": self.turns_simulated,
            "last_actions": self.actions_log[-1] if self.actions_log else {}
        }
