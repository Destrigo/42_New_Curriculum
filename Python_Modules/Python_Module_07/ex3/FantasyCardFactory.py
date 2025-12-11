from .CardFactory import CardFactory
from ..ex0.Card import Card
from ..ex0.CreatureCard import CreatureCard
from ..ex1.SpellCard import SpellCard
from ..ex1.ArtifactCard import ArtifactCard
from typing import Dict, List
import random

class FantasyCardFactory(CardFactory):
    def __init__(self):
        self.creature_types = ["dragon", "goblin"]
        self.spell_types = ["fireball", "icebolt"]
        self.artifact_types = ["mana_ring", "healing_staff"]

    def create_creature(self, name_or_power) -> Card:
        name = name_or_power if isinstance(name_or_power, str) else "Creature"
        return CreatureCard(name=name, cost=random.randint(1,5), rarity="Rare",
                            attack=random.randint(1,7), health=random.randint(1,7))

    def create_spell(self, name_or_power) -> Card:
        return SpellCard(name=name_or_power, cost=3, rarity="Common", effect_type="damage")

    def create_artifact(self, name_or_power) -> Card:
        return ArtifactCard(name=name_or_power, cost=2, rarity="Uncommon", durability=3, effect="+1 mana per turn")

    def create_themed_deck(self, size: int) -> Dict:
        deck = []
        for _ in range(size):
            deck.append(self.create_creature(random.choice(self.creature_types)))
            deck.append(self.create_spell(random.choice(self.spell_types)))
            deck.append(self.create_artifact(random.choice(self.artifact_types)))
        return {"deck": deck}

    def get_supported_types(self) -> Dict:
        return {
            "creatures": self.creature_types,
            "spells": self.spell_types,
            "artifacts": self.artifact_types
        }
