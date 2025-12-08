class GardenError(Exception):
    """base error"""
    pass


class PlantError(GardenError):
    """Plant error"""
    pass


class WaterError(GardenError):
    """Water error"""
    pass


def raise_plant_error():
    raise PlantError("The tomato plant is wilting!")


def raise_water_error():
    raise WaterError("Not enough water in the tank!")


def test_custom_errors():
    print("=== Custom Garden Errors Demo ===")
    print("")

    print("Testing PlantError...")
    try:
        raise_plant_error()
    except PlantError as e:
        print(f"Caught PlantError: {e}")

    print("")
    print("Testing WaterError...")
    try:
        raise_water_error()
    except WaterError as e:
        print(f"Caught WaterError: {e}")

    print("")
    print("Testing catching all garden errors...")
    try:
        raise_plant_error()
    except GardenError as e:
        print(f"Caught a garden error: {e}")
    try:
        raise_water_error()
    except GardenError as e:
        print(f"Caught a garden error: {e}")
    print("")
    print("All custom error types work correctly!")

# if __name__ == "__main__":
#     test_custom_errors()
