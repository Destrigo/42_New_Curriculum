import sys
from .constrained_decoder import Decoder
from .parser import Parser
import json
import time


if __name__ == "__main__":
    # start main
    start_time = time.time()
    try:
        parser = Parser(sys.argv[2], sys.argv[4])
        decoder = Decoder(parser.prompt_list, parser.func_list)
        outputs = []
        decoded = decoder.decode()

        for prompt, decoded_func in zip(parser.prompt_list, decoded):
            func_obj = json.loads(decoded_func)
            func_obj = {"prompt": prompt, **func_obj}
            priority = ["prompt", "fn_name"]
            ordered_func_obj = dict(
                sorted(
                    func_obj.items(),
                    key=lambda item: priority.index(item[0]) if item[0]
                    in priority else len(priority) + 1
                )
            )
            outputs.append(ordered_func_obj)
        with open(sys.argv[6], "w") as f:
            json.dump(outputs, f, indent=2)
    except Exception as e:
        print(e)
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.2f} seconds")
