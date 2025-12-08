class Plant():
    def __init__(self, name: str, height: int, days: int):
        """store info"""
        self.name = name
        self.days = days
        self.height = height

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
    plant1 = Plant("Rose", 25, 30)
    print("=== Day 1 ===")
    plant1.get_info()
    day1_height = plant1.height
    print("=== Day 7 ===")
    plant1.grow(6)
    plant1.age(6)
    plant1.get_info()
    print(f"Growth this week: {plant1.height - day1_height}")
