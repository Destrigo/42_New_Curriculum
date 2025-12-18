def ft_count_harvest_iterative() -> None:
    """count from 1"""
    day = int(input("Days until harvest: "))
    i = 1
    while i <= day:
        print(f"Day {i}")
        i += 1
    print("Harvest time!")
