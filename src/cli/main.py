# src/cli/main.py
import argparse
import sys

from src.config.settings import get_settings # For API key check later
from src.utils.file_operations import read_file, write_file # We'll create this small util
from src.ai.reasoning_agent import ReasoningAgent
from src.core.parser import parse_instructions
from src.core.injector import apply_instructions

# Placeholder for file_operations, create this file next:
# src/utils/file_operations.py
# def read_file(filepath: str) -> str: ...
# def write_file(filepath: str, content: str) -> None: ...


def main():
    parser = argparse.ArgumentParser(description="CodeSlinger: AI-powered code transformation tool.")
    parser.add_argument(
        "original_file",
        help="Path to the Python file with the original code."
    )
    parser.add_argument(
        "suggestion_file",
        help="Path to the Python file with the AI's suggested code."
    )
    parser.add_argument(
        "-o", "--output_file",
        help="Path to write the modified code. Prints to stdout if not provided.",
        default=None
    )
    # Later, we can add arguments for verbosity, model selection, etc.

    args = parser.parse_args()

    print(f"Original file: {args.original_file}")
    print(f"Suggestion file: {args.suggestion_file}")
    print(f"Output file: {args.output_file if args.output_file else 'stdout'}")

    # --- Begin application logic (to be expanded) ---
    try:
        # 1. Load settings (primarily for API key)
        settings = get_settings()
        if not settings.openai_api_key:
            print("Error: OpenAI API key not found. Please set it in your .env file or environment variables.", file=sys.stderr)
            sys.exit(1)

        # 2. Read input files (We'll need to create src/utils/file_operations.py)
        # original_code = read_file(args.original_file)
        # suggested_code = read_file(args.suggestion_file)
        
        # For now, let's use placeholder content to test the flow without file I/O
        original_code = "def hello():\n    print('world')"
        suggested_code = "def hello():\n    # A greeting\n    print('world!')"
        print("\n--- Using placeholder code for now ---")
        print("Original Code:\n", original_code)
        print("Suggested Code:\n", suggested_code)
        print("--------------------------------------\n")


        # 3. Initialize ReasoningAgent
        agent = ReasoningAgent() # API key is checked in its __init__

        # 4. Get transformation instructions
        # print("Asking AI for transformation instructions...")
        # instructions_str = agent.get_instructions(original_code, suggested_code)
        
        # Placeholder instructions_str to avoid API call during CLI dev
        instructions_str = "INSERT 2:     # A greeting\nDELETE 2\nINSERT 3:     print('world!')" # Example
        print(f"Raw Instructions from AI (placeholder):\n{instructions_str}\n")

        if instructions_str.startswith("ERROR:") or not instructions_str.strip():
            print(f"Could not get valid instructions: {instructions_str}", file=sys.stderr)
            sys.exit(1)
        if instructions_str.upper() == "NO CHANGES":
            print("AI reported NO CHANGES needed.")
            modified_code = original_code
        else:
            # 5. Parse instructions
            parsed_instr = parse_instructions(instructions_str)
            if not parsed_instr and instructions_str.upper() != "NO CHANGES": # Should be caught above, but defensive
                print("Failed to parse instructions.", file=sys.stderr)
                sys.exit(1)
            print(f"Parsed Instructions: {parsed_instr}\n")

            # 6. Apply instructions
            modified_code = apply_instructions(original_code, parsed_instr)
        
        # 7. Output the result
        if args.output_file:
            # write_file(args.output_file, modified_code)
            # print(f"Modified code written to {args.output_file}")
            print(f"--- Output (Placeholder: would write to {args.output_file}) ---")
            print(modified_code)
            print("----------------------------------------------------------")
        else:
            print("--- Modified Code (stdout) ---")
            print(modified_code)
            print("------------------------------")

    except ValueError as ve: # For API key issues from ReasoningAgent init
        print(f"Configuration Error: {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()