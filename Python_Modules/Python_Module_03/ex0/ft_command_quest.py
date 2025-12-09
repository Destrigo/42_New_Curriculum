import sys

if __name__ == "__main__":
    """first try"""
    arg = len(sys.argv)
    if arg == 1:
        print("Need some input buddy")
    print(f"Program name: {sys.argv[0]}")
    i = 1
    while i < arg:
        print(f"Argument {i}: {sys.argv[i]}")
        i += 1
    print(f"Total arguments: {i}")