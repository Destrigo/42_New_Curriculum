class Plant():
    def __init__(self, name: str, height: int, days: int):
        """store info"""
        self.name = name
        self.days = days
        self.height = height
        print(f"Created: {self.name} ({self.height}cm, {self.days} days old)")

    def grow(self, cm: int):
        """plant grows in height"""
        self.height += cm

    def age(self, duration: int):
        """plant gets old"""
        self.days += duration

    def get_info(self):
        """print info"""
        print(f"{self.name}: {self.height}cm, {self.days} days old")


if __name__ == "__main__":
    """program"""
    counter = 0
    print("=== Plant Factory Output ===")
    p1 = Plant("Rose", 25, 30)
    p2 = Plant("Oak", 200, 365)
    p3 = Plant("Cactus", 5, 90)
    p4 = Plant("Sunflower", 80, 45)
    p5 = Plant("Fern", 15, 120)
    print(f"Total plants created: {counter}")
