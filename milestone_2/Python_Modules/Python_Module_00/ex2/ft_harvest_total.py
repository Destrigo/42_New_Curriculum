def ft_harvest_total() -> None:
    """ask for lenght and width and print area"""
    day = int(input("Day 1 harvest: "))
    tot = 0
    tot += day
    day = int(input("Day 2 harvest: "))
    tot += day
    day = int(input("Day 3 harvest: "))
    tot += day
    print(f"Total harvest: {tot}")
