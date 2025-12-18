from functools import reduce, partial, lru_cache, singledispatch
import operator
from typing import Callable, List


def spell_reducer(spells: List[int], operation: str) -> int:
    """
    Reduce spell powers using the specified operation.
    Supports: add, multiply, max, min
    """
    ops = {
        "add": operator.add,
        "multiply": operator.mul,
        "max": max,
        "min": min
    }
    if operation not in ops:
        raise ValueError(f"Unsupported operation: {operation}")
    return reduce(ops[operation], spells)


def partial_enchanter(base_enchantment: Callable) -> dict[str, Callable]:
    """
    Create partial enchantments for fire, ice, and lightning.
    Assumes base_enchantment(power, element, target)
    """
    return {
        'fire_enchant': partial(base_enchantment, power=50, element='fire'),
        'ice_enchant': partial(base_enchantment, power=50, element='ice'),
        'lightning_enchant': partial(base_enchantment,
                                     power=50,
                                     element='lightning')
    }


@lru_cache(maxsize=None)
def memoized_fibonacci(n: int) -> int:
    """
    Return nth Fibonacci number using lru_cache for memoization.
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return memoized_fibonacci(n-1) + memoized_fibonacci(n-2)


def spell_dispatcher() -> Callable:
    """
    Single-dispatch spell system for int, str, and list types.
    """
    @singledispatch
    def dispatch(arg):
        return f"Unknown spell type: {type(arg)}"

    @dispatch.register
    def _(arg: int):
        return f"Damage spell deals {arg} damage!"

    @dispatch.register
    def _(arg: str):
        return f"Enchantment applied: {arg}"

    @dispatch.register
    def _(arg: list):
        results = [f"Multi-cast spell hits for {x}" for x in arg]
        return results

    return dispatch


if __name__ == "__main__":
    print("Testing spell reducer...")
    spells = [10, 20, 30, 40]
    print("Sum:", spell_reducer(spells, "add"))
    print("Product:", spell_reducer(spells, "multiply"))
    print("Max:", spell_reducer(spells, "max"))
    print("Min:", spell_reducer(spells, "min"))

    print("\nTesting partial enchanter...")

    def base_enchantment(target, power, element):
        return f"{element.capitalize()} spell of {power} power hits {target}"

    partials = partial_enchanter(base_enchantment)
    print(partials['fire_enchant']("Dragon"))
    print(partials['ice_enchant']("Goblin"))
    print(partials['lightning_enchant']("Orc"))

    print("\nTesting memoized fibonacci...")
    print("Fib(10):", memoized_fibonacci(10))
    print("Fib(15):", memoized_fibonacci(15))

    print("\nTesting spell dispatcher...")
    dispatcher = spell_dispatcher()
    print(dispatcher(50))
    print(dispatcher("Flaming Sword"))
    print(dispatcher([10, 20, 30]))
