from abc import ABC, abstractmethod
from ex0.Card import Card
from typing import Dict


class CardFactory(ABC):
    @abstractmethod
    def create_creature(self, name_or_power) -> Card:
        pass

    @abstractmethod
    def create_spell(self, name_or_power) -> Card:
        pass

    @abstractmethod
    def create_artifact(self, name_or_power) -> Card:
        pass

    @abstractmethod
    def create_themed_deck(self, size: int) -> Dict:
        pass

    @abstractmethod
    def get_supported_types(self) -> Dict:
        pass
