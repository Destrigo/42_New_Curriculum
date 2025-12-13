from .EliteCard import EliteCard


class DummyEnemy:
    def __init__(self, name: str):
        self.name = name


def main():
    print("=== DataDeck Ability System ===")

    # Print capabilities
    print("EliteCard capabilities:")
    print("- Card: ['play', 'get_card_info', 'is_playable']")
    print("- Combatable: ['attack', 'defend', 'get_combat_stats']")
    print("- Magical: ['cast_spell', 'channel_mana', 'get_magic_stats']")

    arcane_warrior = EliteCard(
        name="Arcane Warrior",
        cost=4,
        rarity="Epic",
        attack=5,
        health=7,
        base_mana=4,
    )

    print("Playing Arcane Warrior (Elite Card):")

    # Combat phase
    print("Combat phase:")
    enemy = DummyEnemy("Enemy")
    attack_result = arcane_warrior.attack(enemy)
    print("Attack result:", attack_result)
    defense_result = arcane_warrior.defend(5)
    print("Defense result:", defense_result)

    # Magic phase
    print("Magic phase:")
    # Cast Fireball against two dummy targets
    spell_result = arcane_warrior.cast_spell("Fireball",
                                             [DummyEnemy("Enemy1"),
                                              DummyEnemy("Enemy2")])
    # If cast_spell failed because of mana shortage.
    if spell_result.get("mana_used", 0) == 0:
        # channel 3 mana to reach total 7 as in the example
        channel_result = arcane_warrior.channel_mana(3)
        # cast again
        spell_result = arcane_warrior.cast_spell("Fireball",
                                                 [DummyEnemy("Enemy1"),
                                                  DummyEnemy("Enemy2")])
        print("Spell cast:", spell_result)
        print("Mana channel:", channel_result)
    else:
        print("Spell cast:", spell_result)
        channel_result = arcane_warrior.channel_mana(3)
        print("Mana channel:", channel_result)

    print("Multiple interface implementation successful!")


if __name__ == "__main__":
    main()
