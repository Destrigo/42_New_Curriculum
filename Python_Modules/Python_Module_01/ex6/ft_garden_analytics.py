class Plant:
    def __init__(self, name, height, days):
        self.name = name
        self.height = height
        self.days = days

    def grow(self):
        self.height = self.height + 1
        print(self.name, "grew 1cm")

    def summary(self):
        print(self.name + ": " + str(self.height) + "cm")


class FloweringPlant(Plant):
    def __init__(self, name, height, days, flower_color):
        super().__init__(name, height, days)
        self.flower_color = flower_color
        self.blooming = True

    def summary(self):
        if self.blooming:
            print(self.name + ": " + str(self.height) + "cm, "
                  + self.flower_color + " flowers (blooming)")
        else:
            print(self.name + ": " + str(self.height) + "cm, "
                  + self.flower_color + " flowers (not blooming)")


class PrizeFlower(FloweringPlant):
    def __init__(self, name, height, days, flower_color, prize_points):
        super().__init__(name, height, days, flower_color)
        self.prize_points = prize_points

    def summary(self):
        FloweringPlant.summary(self)
        print("Prize points:", self.prize_points)


class Garden:
    def __init__(self, owner):
        self.owner = owner
        self.plants = [None, None, None, None, None, None, None, None]
        self.count = 0
        self.total_growth = 0

    def add_plant(self, plant):
        self.plants[self.count] = plant
        self.count = self.count + 1
        print("Added", plant.name, "to", self.owner + "'s garden")

    def grow_all(self):
        print(self.owner, "is helping all plants grow...")
        i = 0
        while i < self.count:
            plant = self.plants[i]
            plant.grow()
            self.total_growth = self.total_growth + 1
            i = i + 1

    def report(self):
        print("=== " + self.owner + "'s Garden Report ===")
        print("Plants in garden:")
        i = 0
        while i < self.count:
            self.plants[i].summary()
            i = i + 1
        print("Plants added:", self.count,
              "Total growth:", self.total_growth, "cm")


class GardenManager:
    def __init__(self):
        self.owners = ["Alice", "Bob"]
        self.gardens = [None, None]

    class GardenStats:
        def __init__(self, garden):
            self.garden = garden

        def type_counts(self):
            regular = 0
            flowering = 0
            prize = 0
            i = 0
            while i < self.garden.count:
                p = self.garden.plants[i]
                cname = p.__class__.__name__
                if cname == "PrizeFlower":
                    prize = prize + 1
                elif cname == "FloweringPlant":
                    flowering = flowering + 1
                else:
                    regular = regular + 1
                i = i + 1
            return regular, flowering, prize

        def height_validation_test(self):
            i = 0
            ok = True
            while i < self.garden.count:
                h = self.garden.plants[i].height
                if not GardenManager.validate_height(h):
                    ok = False
                i = i + 1
            return ok

    def find_garden(self, owner):
        i = 0
        while i < 2:
            if self.owners[i] == owner:
                return i
            i = i + 1
        return -1

    def add_garden(self, owner):
        i = self.find_garden(owner)
        if i == -1:
            return None
        g = Garden(owner)
        self.gardens[i] = g
        return g

    def add_plant_to_garden(self, owner, plant):
        i = self.find_garden(owner)
        if i == -1:
            return
        g = self.gardens[i]
        g.add_plant(plant)

    def grow_garden(self, owner, amount):
        i = self.find_garden(owner)
        if i == -1:
            return
        self.gardens[i].grow_all()

    def generate_report_for(self, owner):
        i = self.find_garden(owner)
        if i == -1:
            print("No garden for", owner)
            return
        garden = self.gardens[i]
        garden.report()
        stats = GardenManager.GardenStats(garden)
        r, f, p = stats.type_counts()
        print("Plant types:", r, "regular,", f, "flowering,", p,
              "prize flowers")
        print("Height validation test:", stats.height_validation_test())

    def generate_overall_scores(self):
        scores = ["", ""]
        i = 0
        while i < 2:
            garden = self.gardens[i]
            if garden is None:
                scores[i] = 0
            else:
                score = 0
                j = 0
                while j < garden.count:
                    p = garden.plants[j]
                    score = score + p.height
                    if p.__class__.__name__ == "PrizeFlower":
                        score = score + p.prize_points * 2
                    j = j + 1
                scores[i] = score
            i = i + 1
        return scores

    @classmethod
    def create_garden_network(cls):
        manager = cls()
        manager.add_garden("Alice")
        manager.add_garden("Bob")
        manager.add_plant_to_garden("Alice",
                                    Plant("Oak Tree", 100, 10))
        manager.add_plant_to_garden("Alice",
                                    FloweringPlant("Rose", 25, 10, "red"))
        manager.add_plant_to_garden("Alice",
                                    PrizeFlower("Sunflower", 50,
                                                120, "yellow", 10))
        manager.add_plant_to_garden("Bob",
                                    Plant("Bonsai", 30, 60))
        manager.add_plant_to_garden("Bob",
                                    FloweringPlant("Tulip", 10, 90, "pink"))
        return manager

    @staticmethod
    def validate_height(h):
        return h >= 0

    @staticmethod
    def format_scores(a, b):
        print("Garden scores - Alice:", a, "Bob:", b)


if __name__ == "__main__":
    print("=== Garden Management System Demo ===")
    print("")
    manager = GardenManager.create_garden_network()
    print("")
    manager.grow_garden("Alice", 1)
    print("")
    manager.generate_report_for("Alice")
    print("")
    scores = manager.generate_overall_scores()
    print("")
    GardenManager.format_scores(scores[0], scores[1])
    print("Total gardens managed:", 2)
