class Plant():
    def __init__(self, name: str):
        """store info"""
        self.name = name


def water_plants(plant_list: list):
    """should water plants"""
    print("Opening watering system!")
    try:
        for plant in plant_list:
            print(f"Watering this plant: {plant.name}")
    except AttributeError:
        print(f"Error: Cannot water {plant} - invalid plant!")
    finally:
        print("Closing watering system! (cleanup)")


def test_watering_system():
    """testing"""
    print("=== Garden Watering System ===")
    lst1 = [Plant, Plant, Plant]
    lst2 = [str, str, int]
    lst1[0] = Plant("Rose")
    lst1[1] = Plant("Cactus")
    lst1[2] = Plant("Yaya")
    lst2[0] = "string"
    lst2[1] = "Rose"
    lst2[2] = 50
    print("")
    water_plants(lst1)
    print("Watering completed successfully!")
    print("")
    print("Testing with error...")
    water_plants(lst2)

    print("")
    print("Cleanup always happens, even with errors!")


# if __name__ == "__main__":
#     test_watering_system()
