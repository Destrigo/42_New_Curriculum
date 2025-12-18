from .EliteCard import EliteCard


class DummyEnemy:
    def __init__(self, name: str):
        self.name = name


def main():
    print("=== DataDeck Ability System ===")

    print("EliteCard capabilities:")
    print("- Card: ['play', 'get_card_info', 'is_playable']")
    print("- Combatable: ['attack', 'defend', 'get_combat_stats']")
    print("- Magical: ['cast_spell', 'channel_mana', 'get_magic_stats']")

    arcane_warrior = EliteCard(
        name="Arcane Warrior",
        cost=4,
        rarity="Epic",
        att=5,
        health=7,
        base_mana=4,
    )

    print("Playing Arcane Warrior (Elite Card):")

    print("Combat phase:")
    enemy = DummyEnemy("Enemy")
    attack_result = arcane_warrior.attack(enemy)
    print("Attack result:", attack_result)
    defense_result = arcane_warrior.defend(5)
    print("Defense result:", defense_result)

    print("Magic phase:")
    spell_result = arcane_warrior.cast_spell("Fireball",
                                             [DummyEnemy("Enemy1"),
                                              DummyEnemy("Enemy2")])
    if spell_result.get("mana_used", 0) == 0:
        channel_result = arcane_warrior.channel_mana(3)
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
