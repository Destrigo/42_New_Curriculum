class Plant():
    def __init__(self, name: str, water_level: int, sunlight_hours: int):
        """store info"""
        self.name = name
        self.water_level = water_level
        self.sunlight_hours = sunlight_hours


class GardenError(Exception):
    """base error"""
    pass


class PlantError(GardenError):
    """Plant error"""
    pass


class WaterError(GardenError):
    """Water error"""
    pass


class SunError(GardenError):
    """Sun error"""
    pass


def raise_sun_error():
    raise SunError("Not enough sun!")


def raise_plant_error():
    raise PlantError("The tomato plant is wilting!")


def raise_water_error():
    raise WaterError("Not enough water in the tank!")


class GardenManager():
    """
    • Has methods to add plants, water plants, and check plant health
    • Uses your custom error types from previous exercises
    • Handles different types of errors appropriately
    • Uses try/except/finally blocks where needed
    • Raises its own errors when something is wrong
    • Keeps working even when some operations fail
    """
    def __init__(self):
        self.plants = [Plant, Plant]
        self.added_plants = 0

    def add_plant(self, plant):
        """add plant with errors"""
        print("Adding plants to garden...")
        if not plant.name:
            raise ValueError(f"Error: bad name '{plant.name}'")
        print(f"Added {plant.name} successfully")
        self.plants[self.added_plants] = plant
        self.added_plants += 1

    def water_plants(self):
        """water the plants"""
        print("Watering plants...")
        print("Opening watering system")
        try:
            for plant in self.plants:
                if plant.water_level > 1 and plant.water_level < 10:
                    print(f"Watering {plant.name} - success")
                    plant.water_level += 1
                else:
                    raise ValueError(f"Error: Water level {plant.water_level}"
                                     " is over 10")
        finally:
            print("Closing watering system (cleanup)")

    def check_plant_health(self):
        """check plant health"""
        print("Checkin plant health...")
        for plant in self.plants:
            try:
                if (plant.water_level > 1 and plant.water_level
                   < 10) and plant.sunlight_hours > 2:
                    print(f"{plant.name} healty (water: {plant.water_level}, "
                          "sun: {plant.sunlight_hours})")
                else:
                    if plant.water_level < 1 or plant.water_level > 10:
                        print(f"Error checking {plant.name}: water level is "
                              "out of range")
                        raise_water_error()
                    else:
                        print(f"Error checking {plant.name}: sun level is out "
                              "of range")
                        raise_sun_error()
            except SunError as str:
                print("")
                print("Testing error recovery...")
                print(f"Caught SunError: {str}")
                print("System recovered and continuing...")
            except WaterError as str:
                print("")
                print("Testing error recovery...")
                print(f"Caught WaterError: {str}")
                print("System recovered and continuing...")


# if __name__ == "__main__":
#     gardener = GardenManager()
#     print("")
#     gardener.add_plant(Plant("Rose", 7, 5))
#     print("")
#     gardener.add_plant(Plant("Lettuce", 3, 1))
#     print("")
#     gardener.water_plants
#     print("")
#     gardener.check_plant_health()
#     print("")
