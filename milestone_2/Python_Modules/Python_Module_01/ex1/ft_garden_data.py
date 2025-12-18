class Plant():
    def __init__(self, name: str, height: int, days: int):
        """store info"""
        self.name = name
        self.days = days
        self.height = height


if __name__ == "__main__":
    """program"""
    plant1 = Plant("Rose", 25, 30)
    plant2 = Plant("Sunflower", 80, 45)
    plant3 = Plant("Cactus", 15, 120)
    print("=== Garden Plant Registry ===")
    print(f"{plant1.name}: {plant1.height}cm, {plant1.days} days old")
    print(f"{plant2.name}: {plant2.height}cm, {plant2.days} days old")
    print(f"{plant3.name}: {plant3.height}cm, {plant3.days} days old")
