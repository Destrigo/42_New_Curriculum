from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Magical(ABC):
    """
    Abstract interface for magic-capable cards.
    """

    @abstractmethod
    def cast_spell(self, spell_name: str, targets: List[Any]) -> Dict:
        """
        Cast a named spell against targets.
        """
        pass

    @abstractmethod
    def channel_mana(self, amount: int) -> Dict:
        """
        Channel (gain) mana and return new mana state.
        """
        pass

    @abstractmethod
    def get_magic_stats(self) -> Dict:
        """
        Return magic-related stats (current mana, spell power, etc.).
        """
        pass
