from abc import ABC, abstractmethod
from typing import Dict, Any


class Combatable(ABC):
    """
    Abstract interface for combat-capable cards.
    """

    @abstractmethod
    def attack(self, target: Any) -> Dict:
        """
        Execute an attack against a target.
        """
        pass

    @abstractmethod
    def defend(self, incoming_damage: int) -> Dict:
        """
        Defend against incoming damage and return defense resolution.
        """
        pass

    @abstractmethod
    def get_combat_stats(self) -> Dict:
        """
        Return combat-related stats (attack, health, etc.).
        """
        pass
