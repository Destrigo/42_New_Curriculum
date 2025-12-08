def ft_water_reminder() -> None:
    """as I'm writing this i don't know what it should do"""
    days = int(input("EDays since last watering: "))
    if days > 2:
        print("Water the plants!")
    else:
        print("Plants are fine")
