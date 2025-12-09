import sys
import math


def distance3D(p1: tuple, p2: tuple):
    """return distance"""
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return int(math.sqrt((int(x2) - int(x1))**2 +
                         (int(y2) - int(y1))**2 +
                         (int(z2) - int(z1))**2))


if __name__ == "__main__":
    """first try"""
    print("=== Player Score Analytics ===")
    try:
        arg = sys.argv[1]
    except IndexError:
        print("Give me some input! Example '10,7,9'")
    else:
        x_spawn = 0
        y_spawn = 0
        z_spawn = 0
        spawn_point = (x_spawn, y_spawn, z_spawn,)
        print(f"Spawn created: {spawn_point}")
        x1 = 10
        y1 = 20
        z1 = 5
        p1 = (x1, y1, z1,)
        print(f"Distance between {spawn_point} and {p1}: "
              f"{distance3D(spawn_point, p1)}")
        print("")
        print(f"Parsing coordinates from input: {sys.argv[1]}")
        parsed_list = sys.argv[1].split(",")
        try:
            for x in parsed_list:
                x = int(x)
        except ValueError:
            print("Error parsing coordinates: invalid literal "
                  f"for int() with base 10: {x}")
        parsed_tuple = tuple([x for x in parsed_list])
        print(f"Parsed position: {parsed_tuple}")
        try:
            print(f"Distance between {spawn_point} and {parsed_tuple}: "
                  f"{distance3D(spawn_point, parsed_tuple)}")
        except ValueError:
            print("Wrong parsing!")
            parsed_tuple = (0, 0, 0,)
        print("")
        invalid = "asd,def,ghi"
        print(f"Parsing invalid coordinates: {invalid}")
        invalid_list = invalid.split(",")
        try:
            for x in invalid_list:
                x = int(x)
        except ValueError:
            print("Error parsing coordinates: invalid literal "
                  f"for int() with base 10: {x}")
        x_unpack, y_unpack, z_unpack = parsed_tuple
        print("")
        print("Unpacking demonstation:")
        print(f"Player at x={x_unpack}, y={y_unpack}, z={z_unpack}")
