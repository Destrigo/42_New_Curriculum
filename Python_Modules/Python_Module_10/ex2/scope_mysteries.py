from typing import Callable, Dict


def mage_counter() -> Callable[[], int]:
    """
    Returns a function that counts how many times it has been called.
    Uses closure to persist the count.
    """
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


def spell_accumulator(initial_power: int) -> Callable[[int], int]:
    """
    Returns a function that accumulates spell power over time.
    Each call adds to total power and returns the new total.
    """
    total_power = initial_power

    def accumulator(power_addition: int):
        nonlocal total_power
        total_power += power_addition
        return total_power

    return accumulator


def enchantment_factory(enchantment_type: str) -> Callable[[str], str]:
    """
    Returns a function that applies a given enchantment to an item.
    """
    def enchant(item_name: str):
        return f"{enchantment_type} {item_name}"
    return enchant


def memory_vault() -> Dict[str, Callable]:
    """
    Returns a dictionary with 'store' and 'recall' functions.
    Maintains a private memory dictionary via closure.
    """
    memory: Dict[str, any] = {}

    def store(key: str, value: any):
        memory[key] = value

    def recall(key: str):
        return memory.get(key, "Memory not found")

    return {'store': store, 'recall': recall}


if __name__ == "__main__":
    print("Testing mage counter...")
    counter = mage_counter()
    print("Call 1:", counter())
    print("Call 2:", counter())
    print("Call 3:", counter())

    print("\nTesting spell accumulator...")
    accumulator = spell_accumulator(10)
    print("Add 5:", accumulator(5))
    print("Add 15:", accumulator(15))
    print("Add 20:", accumulator(20))

    print("\nTesting enchantment factory...")
    flaming = enchantment_factory("Flaming")
    frozen = enchantment_factory("Frozen")
    print(flaming("Sword"))
    print(frozen("Shield"))

    print("\nTesting memory vault...")
    vault = memory_vault()
    vault['store']("secret_spell", "Invisibility")
    vault['store']("artifact", "Orb of Power")
    print(vault['recall']("secret_spell"))
    print(vault['recall']("artifact"))
    print(vault['recall']("unknown_key"))
