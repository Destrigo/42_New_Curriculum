import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from .constrained_decoder import Decoder
from .parser import Parser
from .models import validate_output


def create_validated_output(
    prompt: str,
    func_obj: Dict[str, Any]
) -> Any:
    """Create and validate output object.
    Args:
        prompt: Original user prompt
        func_obj: Decoded function object
    Returns:
        Validated output dictionary
    Raises:
        ValueError: If output validation fails
    """
    output_data = {
        "prompt": prompt,
        "fn_name": func_obj["fn_name"],
        "args": func_obj.get("args", {})
    }

    # Validate with Pydantic
    validation_result = validate_output(output_data)

    if not validation_result.valid:
        errors_str = "; ".join(validation_result.errors)
        raise ValueError(f"Output validation failed: {errors_str}")

    # Return validated data as dict
    return validation_result.data.model_dump()


def main() -> int:
    """Main function.
    Returns:
        Exit code (0 for success, 1 for error)
    """
    start_time = time.time()
    try:
        # Parse command line arguments
        if len(sys.argv) < 7:
            print("Usage: python -m src --input <prompts.json> "
                  "--input <functions.json> --output <output.json>")
            return 1

        prompt_file = sys.argv[2]
        func_file = sys.argv[4]
        output_file = sys.argv[6]

        # Parse and validate input files
        parser = Parser(prompt_file, func_file)

        # Initialize decoder
        decoder = Decoder(parser.prompt_list, parser.func_list)

        # Process prompts
        outputs: List[Dict[str, Any]] = []
        decoded = decoder.decode()

        for prompt, decoded_func in zip(parser.prompt_list, decoded):
            func_obj = json.loads(decoded_func)
            # Create and validate output
            validated_output = create_validated_output(prompt, func_obj)
            outputs.append(validated_output)
        # Write output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=2)
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return 1
    except ValueError as e:
        print(f"Validation Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 1
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    sys.exit(main())
