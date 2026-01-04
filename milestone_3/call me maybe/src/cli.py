# src/cli.py
import argparse
from .pipeline import run_pipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="Function Calling LLM: translate natural language prompts "
                    "into structured function calls."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/input/function_calling_tests.json",
        help="Path to the input JSON file with prompts"
    )
    parser.add_argument(
        "--functions",
        type=str,
        default="data/input/function_definitions.json",
        help="Path to the input JSON file with function definitions"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/output/function_calling_results.json",
        help="Path to the output JSON file where results will be written"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    run_pipeline(input_file=args.input,
                 functions_file=args.functions,
                 output_file=args.output)


if __name__ == "__main__":
    main()
