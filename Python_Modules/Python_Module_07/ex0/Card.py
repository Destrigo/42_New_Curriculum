from abc import ABC, abstractmethod


class Card(ABC):
    def __init__(self, name: str, cost: int, rarity: str) -> None:
        """init"""
        self.name = name
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def play(self, game_state: dict) -> dict:
        """prototype"""
        pass

    def get_card_info(self) -> dict:
        """ print card info"""
        return {
            "name": self.name,
            "cost": self.cost,
            "rarity": self.rarity,
            "type": self.__class__.__name__.replace("Card", "")
        }

    def is_playable(self, available_mana: int) -> bool:
        """for later"""
        return available_mana >= self.cost
