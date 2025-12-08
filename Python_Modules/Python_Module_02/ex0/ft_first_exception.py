def check_temperature(temp_str: str) -> int | None:
    """
    Takes a string input from the user
    • Tries to convert it to a number
    • Checks if the temperature is reasonable for plants (0 to 40 degrees)
    • Returns the temperature if its valid
    • Handles the case when the input isnt a number
    • Handles the case when the temperature is too high or too low"""
    print(f"Testing temperature: {temp_str}")
    try:
        temp = int(temp_str)
    except AttributeError:
        print(f"Error: {temp_str} in not a number")
        return None

    if temp > 40:
        print(f"Error: {temp}°C is too hot for plants (max 40°C)")
        return None

    elif temp < 0:
        print(f"Error: {temp}°C is too cold for plants (min 0°C)")
        return None

    print(f"Temperature {temp}°C is perfect for plants!")
    return temp


def test_temperature_input():
    print("=== Garden Temperature Checker ===")
    tests = ["25", "abc", "100", "-50"]
    for t in tests:
        check_temperature(t)
    print("All tests completed - program didn't crash!")
