import alchemy
import alchemy.elements
    

if __name__ == "__main__":
    """main test"""
    print("=== Sacred Scroll Mastery ===\n")

    print("Testing direct module access:")

    print("alchemy.elements.create_fire():", alchemy.elements.create_fire())
    print("alchemy.elements.create_water():", alchemy.elements.create_water())
    print("alchemy.elements.create_earth():", alchemy.elements.create_earth())
    print("alchemy.elements.create_air():", alchemy.elements.create_air())
    print("\nTesting package-level access (controlled by __init__.py):")

    def test_package_call(func_name: str) -> None:
        try:
            func = getattr(alchemy, func_name)
            result = func()
            print(f"alchemy.{func_name}():", result)
        except AttributeError:
            print(f"alchemy.{func_name}(): AttributeError - not exposed")

    test_package_call("create_fire")
    test_package_call("create_water")
    test_package_call("create_earth")
    test_package_call("create_air")

    print("\nPackage metadata:")
    print("Version:", alchemy.__version__)
    print("Author:", alchemy.__author__)