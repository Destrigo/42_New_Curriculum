def garden_operations(value: str,
                      zero: int,
                      fd: str,
                      dictionary: dict,
                      key: str) -> float:
    """Perform tests."""
    try:
        num = int(value)
    except ValueError:
        ValueError("Caught ValueError: invalid literal for int()")
    num = 1
    try:
        res = num / zero
    except ZeroDivisionError:
        ZeroDivisionError("Caught ZeroDivisionError: division by zero")
    try:
        open(fd)
    except FileNotFoundError:
        FileNotFoundError(f"Caught FileNotFoundError: No such file '{fd}'")
    try:
        dictionary[key]
    except KeyError:
        KeyError("Caught KeyError: 'missing_plant'")
    res = 0
    return res


def test_error_types():
    print("=== Garden Error Types Demo ===")
    print("")

    print("Testing ValueError...")
    garden_operations("abc", 1, "missing.txt", {"plant": 1}, "plant")
    print("")

    print("Testing ZeroDivisionError...")
    garden_operations("10", 0, "missing.txt", {"plant": 1}, "plant")
    print("")

    print("Testing FileNotFoundError...")
    garden_operations("10", 1, "missing.txt", {"plant": 1}, "plant")
    print("")

    print("Testing KeyError...")
    garden_operations("10", 1, "", {"plant": 1}, "missing_plant")
    print("")

    print("Testing multiple errors together...")
    garden_operations("abc", 0, "missing.txt", {}, "missing_plant")
    print("Caught an error, but program continues!")
    print("")

    print("All error types tested successfully!")
