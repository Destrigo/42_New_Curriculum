class Plant():
    def __init__(self, name: str, water_level: int, sunlight_hours: int):
        """store info"""
        self.name = name
        self.water_level = water_level
        self.sunlight_hours = sunlight_hours


def check_plant_health(plant_name, water_level, sunlight_hours):
    """
    • Checks if the plant name is valid (not empty)
    • Checks if water level is reasonable (between 1 and 10)
    • Checks if sunlight hours are reasonable (between 2 and 12)
    • Raises appropriate errors with helpful messages when something is wrong
    • Returns a success message if everything is okay"""
    if not plant_name:
        raise ValueError(f"Error: bad name '{plant_name}'")
    if water_level < 1 or water_level > 10:
        raise ValueError(f"Error: Water level {water_level} is "
                         "out of range (1-10)")
    if sunlight_hours < 2 or sunlight_hours > 12:
        raise ValueError(f"Error: Sunlight hours {sunlight_hours} is out "
                         "of range (2-12)")
    print(f"Plant {plant_name} is healthy")


def test_plant_checks():
    """
    • Testing with good values (should work fine)
    • Testing with bad plant name (should raise ValueError)
    • Testing with bad water level (should raise ValueError)
    • Testing with bad sunlight hours (should raise ValueError)
    • Catching and handling each error appropriately"""
    try:
        p1 = Plant("Rose", 5, 5)
        check_plant_health(p1.name, p1.water_level, p1.sunlight_hours)
    except ValueError as e:
        print(e)
    print("")

    try:
        p1 = Plant("", 5, 5)
        check_plant_health(p1.name, p1.water_level, p1.sunlight_hours)
    except ValueError as e:
        print(e)
    print("")

    try:
        p1 = Plant("Rose", 20, 5)
        check_plant_health(p1.name, p1.water_level, p1.sunlight_hours)
    except ValueError as e:
        print(e)
    print("")

    try:
        p1 = Plant("Rose", 7, 1)
        check_plant_health(p1.name, p1.water_level, p1.sunlight_hours)
    except ValueError as e:
        print(e)
    print("")

# if __name__ == "__main__":
#     test_plant_checks()
