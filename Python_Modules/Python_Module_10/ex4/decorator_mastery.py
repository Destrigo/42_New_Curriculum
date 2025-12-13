import time
import functools


def spell_timer(func: callable) -> callable:
    """
    Decorator that times a function execution and prints before/after messages.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Casting {func.__name__}...")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Spell completed in {end_time - start_time:.3f} seconds")
        return result
    return wrapper


def power_validator(min_power: int) -> callable:
    """
    Parameterized decorator that checks if the
    first argument (power) is >= min_power.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) > 0 and args[0] < min_power:
                return "Insufficient power for this spell"
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_spell(max_attempts: int) -> callable:
    """
    Decorator that retries a function if it raises an exception.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt < max_attempts:
                        print(f"Spell failed, retrying... "
                              f"(attempt {attempt}/{max_attempts})")
                    else:
                        return (f"Spell casting failed "
                                f"after {max_attempts} attempts")
        return wrapper
    return decorator


class MageGuild:
    @staticmethod
    def validate_mage_name(name: str) -> bool:
        """
        Validates mage name: at least 3 characters, letters and spaces only.
        """
        return len(name) >= 3 and all(c.isalpha() or c.isspace() for c in name)

    @power_validator(min_power=10)
    def cast_spell(self, spell_name: str, power: int) -> str:
        """
        Casts a spell with validation on power level.
        """
        return f"Successfully cast {spell_name} with {power} power"


if __name__ == "__main__":
    print("Testing spell timer...")

    @spell_timer
    def fireball():
        time.sleep(0.1)
        return "Fireball cast!"

    result = fireball()
    print("Result:", result)

    print("\nTesting MageGuild...")
    guild = MageGuild()
    print(MageGuild.validate_mage_name("Gandalf"))  # True
    print(MageGuild.validate_mage_name("Al"))       # False

    print(guild.cast_spell("Lightning", 15))        # Successful
    print(guild.cast_spell("Ice Shard", 5))         # Insufficient power

    print("\nTesting retry_spell...")

    counter = 0

    @retry_spell(max_attempts=3)
    def unstable_spell():
        nonlocal counter
        counter += 1
        if counter < 3:
            raise ValueError("Spell fizzled")
        return "Spell succeeded!"

    # Call unstable_spell (requires nonlocal workaround inside function)
    try:
        print(unstable_spell())
    except SyntaxError:
        # Alternatively, demonstrate retry with a simple function
        @retry_spell(3)
        def test_spell():
            import random
            if random.random() < 0.7:
                raise Exception("Random spell failure")
            return "Spell succeeded randomly!"
        print(test_spell())
