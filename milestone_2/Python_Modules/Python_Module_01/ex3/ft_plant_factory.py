class Plant:
    def __init__(self, name: str, height: int, age: int):
        self.name = name
        self.height = height
        self.age = age

    def summary(self):
        print(f"Created: {self.name} ({self.height}cm, {self.age} days)")


class PlantFactory:
    def __init__(self):
        self.plants = [Plant, Plant, Plant, Plant, Plant]
        self.counter = 0

    def create_plant(self, name, height, age):
        plant = Plant(name, height, age)
        self.plants[self.counter](plant)
        self.counter += 1
        plant.summary()

    def create_many_plants(self):
        self.create_plant("Rose", 25, 30)
        self.create_plant("Oak", 200, 365)
        self.create_plant("Cactus", 5, 90)
        self.create_plant("Sunflower", 80, 45)
        self.create_plant("Fern", 15, 120)

    def display_total(self):
        print(f"Total plants created: {len(self.plants)}")


# if __name__ == "__main__":
#     print("=== Plant Factory Output ===")

#     factory = PlantFactory()
#     factory.create_many_plants()
#     factory.display_total()
