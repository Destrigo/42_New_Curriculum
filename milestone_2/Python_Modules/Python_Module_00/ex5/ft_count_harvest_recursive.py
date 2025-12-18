def ft_count_harvest_recursive() -> None:
    """count from 1"""
    days = int(input("Days until harvest: "))

    def count(day, limit):
        if day > limit:
            print("Harvest time!")
            return
        print(f"Day {day}")
        count(day + 1, limit)

    count(1, days)
