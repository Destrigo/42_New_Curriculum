from .CreatureCard import CreatureCard


class DummyTarget:
    """Simple enemy"""
    def __init__(self, name: str):
        self.name = name
        self.attack = 3
        self.health = 2


def main() -> None:
    print("=== DataDeck Card Foundation ===")
    print("Testing Abstract Base Class Design:")

    fire_dragon = CreatureCard(
        name="Fire Dragon",
        cost=5,
        rarity="Legendary",
        attack=7,
        health=5
    )

    print("CreatureCard Info:")
    info = fire_dragon.get_card_info()
    info["attack"] = fire_dragon.attack
    info["health"] = fire_dragon.health
    print(info)

    print("Playing Fire Dragon with 6 mana available:")
    print("Playable:", fire_dragon.is_playable(6))
    play_result = fire_dragon.play({})
    print("Play result:", play_result)

    print("Fire Dragon attacks Goblin Warrior:")
    goblin = DummyTarget("Goblin Warrior")
    attack_result = fire_dragon.attack_target(goblin)
    print("Attack result:", attack_result)

    print("Testing insufficient mana (3 available):")
    print("Playable:", fire_dragon.is_playable(3))

    print("Abstract pattern successfully demonstrated!")


if __name__ == "__main__":
    main()
