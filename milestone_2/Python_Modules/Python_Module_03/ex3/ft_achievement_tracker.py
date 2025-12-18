class Player():
    def __init__(self, achiev):
        self.achiev = achiev


if __name__ == "__main__":
    """first try"""
    print("=== Achievement Tracker System ===")
    print("")
    alice = Player(set(["first kill", "level_10",
                        "treasure_hunter", "speed_demon"]))
    bob = Player(set(["first kill", "level_10", "boss_slayer", "collector"]))
    charlie = Player(set(["level_10", "treasure_hunter", "boss_slayer",
                     "speed_demon", "perfectionist"]))
    print(f"Player alice achievements: {alice.achiev}")
    print(f"Player bob achievements: {bob.achiev}")
    print(f"Player charlie achievements: {charlie.achiev}")
    print("")

    print("=== Achievement Analytics ===")
    unique = (alice.achiev).union(bob.achiev)
    unique = unique.union(charlie.achiev)
    print(f"All unique achievements: {unique}")
    print(f"Total unique achievements: {len(unique)}")
    print("")

    inter = (alice.achiev).intersection(bob.achiev)
    inter = unique.intersection(charlie.achiev)
    print(f"Common to all players: {inter}")
    dif = (alice.achiev).difference(bob.achiev)
    dif = unique.difference(charlie.achiev)
    print(f"Rare achievements (1 player): {dif}")
    print("")

    print(f"Alice vs Bob common: {(alice.achiev).intersection(bob.achiev)}")
    print(f"Alice unique: {(alice.achiev).difference(bob.achiev)}")
    print(f"Bob unique: {(bob.achiev).difference(alice.achiev)}")
