import sys
from .parser import Parser
from .engine import Engine

if __name__ == "__main__":
    # start main
    if len(sys.argv) != 3:
        print("Incorrect arguments!")
        exit(1)
    try:
        parser = Parser(sys.argv[2])
        engine = Engine(parser.file_input)
        engine.play()
    except Exception as e:
        print(e)
