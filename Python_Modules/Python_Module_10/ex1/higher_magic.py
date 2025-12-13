from typing import Callable, List


def spell_combiner(spell1: Callable, spell2: Callable) -> Callable:
    """
    Combine two spells into one. Returns a function that calls both spells
    with the same arguments and returns a tuple of their results.
    """
    def combined(*args, **kwargs):
        result1 = spell1(*args, **kwargs)
        result2 = spell2(*args, **kwargs)
        return (result1, result2)
    return combined


def power_amplifier(base_spell: Callable, multiplier: int) -> Callable:
    """
    Amplify the result of a spell by a multiplier.
    Assumes base_spell returns a numeric value.
    """
    def amplified(*args, **kwargs):
        return base_spell(*args, **kwargs) * multiplier
    return amplified


def conditional_caster(condition: Callable, spell: Callable) -> Callable:
    """
    Cast a spell only if a condition function returns True.
    Returns "Spell fizzled" if condition fails.
    """
    def caster(*args, **kwargs):
        if condition(*args, **kwargs):
            return spell(*args, **kwargs)
        else:
            return "Spell fizzled"
    return caster


def spell_sequence(spells: List[Callable]) -> Callable:
    """
    Cast a sequence of spells in order.
    Returns a list of results.
    """
    def sequence(*args, **kwargs):
        return [spell(*args, **kwargs) for spell in spells]
    return sequence


def fireball(target):
    return f"Fireball hits {target}"


def heal(target):
    return f"Heals {target}"


def lightning(target):
    return f"Lightning strikes {target}"


def damage_spell(value):
    return value


def is_enemy(target):
    return target.lower() in ["dragon", "orc", "goblin"]


if __name__ == "__main__":
    print("Testing spell combiner...")
    combined = spell_combiner(fireball, heal)
    result = combined("Dragon")
    print("Combined spell result:", ", ".join(result))

    print("\nTesting power amplifier...")
    base = lambda: 10
    amplified = power_amplifier(base, 3)
    print(f"Original: {base()}, Amplified: {amplified()}")

    print("\nTesting conditional caster...")
    conditional = conditional_caster(is_enemy, fireball)
    print("Casting on Dragon:", conditional("Dragon"))
    print("Casting on Villager:", conditional("Villager"))

    print("\nTesting spell sequence...")
    sequence = spell_sequence([fireball, heal, lightning])
    seq_result = sequence("Orc")
    print("Spell sequence results:", seq_result)
