import sys
from .constrained_decoder import Decoder
from .parser import Parser
import json


if __name__ == "__main__":
    try:
        parser = Parser(sys.argv[2], sys.argv[4])
        decoder = Decoder(parser.prompt_list, parser.func_list)
        outputs = decoder.decode()
        print(outputs)
        # with open(sys.argv[6], "w") as f:
        #     f.write(outputs)
    except Exception as e:
        raise Exception(e)
