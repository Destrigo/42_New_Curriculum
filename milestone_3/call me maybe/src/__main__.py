import sys
from .constrained_decoder import Decoder
from .parser import Parser


if __name__ == "__main__":
    try:
        parser = Parser(sys.argv[2], sys.argv[4])
        decoder = Decoder(parser.prompt_list, parser.func_list)
        outputs = decoder.decode()
        for prompt, output in zip(parser.prompt_list, outputs):
            print(f"Prompt: {prompt}\nOutput: {output}\n")
    except Exception as e:
        raise Exception(e)
