def garden_operations(value: str,
                      zero: int,
                      fd: str,
                      dictionary: dict,
                      key: str) -> float:
    """Perform tests."""
    try:
        num = int(value)
    except ValueError:
        print("Caught ValueError: invalid literal for int()")
        pass
    try:
        num = 1
        res = num / zero
    except ZeroDivisionError:
        print("Caught ZeroDivisionError: division by zero")
        pass
    try:
        open(fd)
    except FileNotFoundError:
        print("Caught FileNotFoundError: No such file 'missing.txt'")
        pass
    try:
        dictionary[key]
    except KeyError:
        print("Caught KeyError: 'missing_plant'")
        pass
    res = 0
    return res


def test_error_types():
    print("=== Garden Error Types Demo ===")
    print("")

    print("Testing ValueError...")
    garden_operations("abc", 1, "ft_different_errors.py",
                      {"plant": 1}, "plant")

    print("")
    print("Testing ZeroDivisionError...")
    garden_operations("10", 0, "ft_different_errors.py", {"plant": 1}, "plant")

    print("")
    print("Testing FileNotFoundError...")
    garden_operations("10", 1, "missing.txt", {"plant": 1}, "plant")

    print("")
    print("Testing KeyError...")
    garden_operations("10", 1, "ft_different_errors.py",
                      {"plant": 1}, "missing_plant")
    print("")

    print("Testing multiple errors together...")
    garden_operations("abc", 0, "missing.txt", {}, "missing_plant")
    print("")

    print("All error types tested successfully!")


if __name__ == "__main__":
    """main"""
    test_error_types()
