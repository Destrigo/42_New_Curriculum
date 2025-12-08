class SafePlant():
    def __init__(self, name: str, height: int, days: int):
        """store info"""
        self.name = name
        print(f"Plant Created: {self.name}")
        self.__height = 0
        self.set_height(height)
        self.__age = 0
        self.set_age(days)

    def set_height(self, new_height):
        """self explanatory"""
        if new_height < 0:
            print("Invalid operation attempted: "
                  f"height {new_height}cm [REJECTED]")
            print("Security: Negative height rejected")
        else:
            self.__height = new_height
            print(f"Height updated: {self.__height}cm [OK]")

    def set_age(self, new_age):
        """self explanatory"""
        if new_age < 0:
            print("Invalid operation attempted: "
                  f"age {new_age}days [REJECTED]")
            print("Security: Negative age rejected")
        else:
            self.__age = new_age
            print(f"Age updated: {self.__age}days [OK]")

    def get_height(self):
        return self.__height

    def get_age(self):
        return self.__age

    def get_info(self):
        """print info"""
        print(f"{self.name}: {self.__height}cm, {self.__age} days old")


if __name__ == "__main__":
    """program"""
    counter = 0
    print("=== Garden Security System ===")
    p1 = SafePlant("Rose", 25, 30)
    p1.set_height(-5)
    height = p1.get_height()
    print(f"{height}")
    p1.set_height(50)
    height = p1.get_height()
    print(f"{height}")
