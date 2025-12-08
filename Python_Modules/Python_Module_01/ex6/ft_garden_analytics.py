class Plant():
    def __init__(self, name: str, height: int, days: int):
        """store info"""
        self.name = name
        self.days = days
        self.height = height

    def grow(self):
        self.height += 1
        print(f"{self.name} grew 1cm")

    def summary(self):
        print(f"{self.name}: {self.height}cm ")


class FloweringPlant(Plant):
    def __init__(self, name: str, height: int, days: int, flower_color: str):
        super().__init__(name, height, days)
        self.flower_color = flower_color
        self.blooming = True

    def summary(self):
        bloom_state = "blooming" if self.blooming else "not blooming"
        print(f"{self.name}: {self.height}cm, "
              f"{self.flower_color} flowers ({bloom_state})")


class PrizeFlower(FloweringPlant):
    def __init__(self, name: str, height: int, flower_color: str,
                 days: int, prize_points: int):
        super().__init__(name, height, days, flower_color)
        self.prize_points = prize_points

    def summary(self):
        base = super().summary()
        return f"{base}, Prize points: {self.prize_points}"


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


class Garden:
    def __init__(self, owner: str):
        self.owner = owner
        self.plants = [Plant]
        self.total_growth = 0

    def add_plant(self, plant):
        self.plants.append(plant)
        print(f"Added {plant.name} to {self.owner}'s garden")

    def grow_all(self):
        print(f"{self.owner} is helping all plants grow...")
        for plant in self.plants:
            plant.grow(plant)
            self.total_growth += 1

    def report(self):
        print(f"=== {self.owner}'s Garden Report ===")
        print("Plants in garden:")
        for plant in self.plants:
            print(f"- {plant.summary()}")
        print(f"Plants added: {len(self.plants)}, "
              f"Total growth: {self.total_growth}cm")


class GardenManager:
    def __init__(self):
        self.gardens = {}

    class GardenStats:
        def __init__(self, garden):
            self.garden = garden

        def count_plants(self):
            return len(self.garden.plants)

        def total_height(self):
            return sum(p.height for p in self.garden.plants)

        def type_counts(self):
            regular = 0
            flowering = 0
            prize = 0
            for p in self.garden.plants:
                if isinstance(p, PrizeFlower):
                    prize += 1
                elif isinstance(p, FloweringPlant):
                    flowering += 1
                else:
                    regular += 1
            return regular, flowering, prize

        def height_validation_test(self):
            return all(GardenManager.validate_height(p.height)
                       for p in self.garden.plants)

    def add_garden(self, owner: str):
        g = Garden(owner)
        self.gardens[owner] = g
        return g

    def add_plant_to_garden(self, owner: str, plant):
        if owner not in self.gardens:
            self.add_garden(owner)
        self.gardens[owner].add_plant(plant)

    def grow_garden(self, owner: str, amount: int):
        if owner in self.gardens:
            self.gardens[owner].grow_all()

    def generate_report_for(self, owner: str):
        if owner not in self.gardens:
            print(f"No garden for {owner}")
            return
        garden = self.gardens[owner]
        garden.report()
        stats = GardenManager.GardenStats(garden)
        regular, flowering, prize = stats.type_counts()
        print(f"Plant types: {regular} regular, {flowering} flowering,"
              f"{prize} prize flowers")
        print(f"Height validation test: {stats.height_validation_test()}")

    def generate_overall_scores(self):
        scores = {}
        for owner, garden in self.gardens.items():
            score = 0
            for p in garden.plants:
                score += p.height
                if isinstance(p, PrizeFlower):
                    score += p.prize_points * 2
            scores[owner] = score
        return scores

    @classmethod
    def create_garden_network(cls):
        manager = cls()
        manager.add_garden("Alice")
        manager.add_garden("Bob")
        manager.add_plant_to_garden("Alice", Plant("Oak Tree", 100, 10))
        manager.add_plant_to_garden("Alice", FloweringPlant("Rose", 25, 10,
                                                            "red"))
        manager.add_plant_to_garden("Alice",
                                    PrizeFlower("Sunflower",
                                                50, 120, "yellow",
                                                prize_points=10))
        manager.add_plant_to_garden("Bob", Plant("Bonsai", 30, 60))
        manager.add_plant_to_garden("Bob", FloweringPlant("Tulip", 10, 90,
                                                          "pink"))
        return manager

    @staticmethod
    def validate_height(h):
        return isinstance(h, int) and h >= 0

    @staticmethod
    def format_scores(scores):
        return ", ".join(f"{k}: {v}" for k, v in scores.items())


if __name__ == "__main__":
    print("=== Garden Management System Demo ===")
    manager = GardenManager.create_garden_network()
    manager.grow_garden("Alice", 1)
    manager.generate_report_for("Alice")
    scores = manager.generate_overall_scores()
    print(f"Garden scores - {GardenManager.format_scores(scores)}")
    print(f"Total gardens managed: {len(manager.gardens)}")
