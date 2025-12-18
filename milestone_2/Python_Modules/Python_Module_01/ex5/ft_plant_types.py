class Plant():
    def __init__(self, name: str, height: int, days: int):
        """store info"""
        self.name = name
        self.days = days
        self.height = height


class Flower(Plant):
    def __init__(self, name: str, height: int, days: int, color: str):
        super().__init__(name, height, days)
        self.color = color
        print(f"{self.name} (Flower): {self.height}cm, "
              f"{self.days} days, {self.color} color")

    def bloom(self):
        print(f"{self.name} is blooming beautifully!")


class Tree(Plant):
    def __init__(self, name: str, height: int, days: int, trunk_diameter: int):
        super().__init__(name, height, days)
        self.trunk_diameter = trunk_diameter
        print(f"{self.name} (Tree): {self.height}cm, "
              f"{self.days} days, {self.trunk_diameter}cm diameter")

    def produce_shade(self):
        """no idea"""
        print(f"{self.name} provides "
              f"{self.trunk_diameter * self.height / 1000 * 3.14} square "
              "meters of shade")


class Vegetable(Plant):
    def __init__(self, name: str, height: int, days: int,
                 harvest_season: str, nutritional_value: str):
        super().__init__(name, height, days)
        self.harvest_season = harvest_season
        self.nutritional_value = nutritional_value
        print(f"{self.name} (Vegetable): {self.height}cm, "
              f"{self.days} days, {self.harvest_season}cm diameter")
        print(f"{self.name} is rich in {self.nutritional_value}")


# if __name__ == "__main__":
#     """program"""
#     print("=== Garden Plant Types ===")
#     print("")
#     rose = Flower("Rose", 25, 30, "red")
#     tulip = Flower("Tulip", 50, 90, "yellow")
#     rose.bloom()
#     tulip.bloom()
#     print("")
#     oak = Tree("Oak", 500, 1825, 50)
#     oak.produce_shade()
#     birch = Tree("birch", 700, 1500, 90)
#     birch.produce_shade()
#     print("")
#     tomato = Vegetable("Tomato", 80, 90, "summer harvest", "vitamin C")
#     cucumber = Vegetable("Cucumber", 50, 120, "fall harvest", "vitamin D")
