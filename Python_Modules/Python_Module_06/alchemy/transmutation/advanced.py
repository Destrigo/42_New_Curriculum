from .basic import lead_to_gold
from ..potions import healing_potion


def philosophers_stone():
    gold_result = lead_to_gold()
    heal_result = healing_potion()
    return (
        "Philosopher's stone created using "
        f"{gold_result} and {heal_result}"
    )


def elixir_of_life():
    return "Elixir of life: eternal youth achieved!"
