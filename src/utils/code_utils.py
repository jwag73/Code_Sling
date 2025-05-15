# src/utils/code_utils.py

def add_line_numbers(code_string: str) -> str:
    """
    Adds line numbers to a given string of code.

    Args:
        code_string: A string containing code, with lines separated by newlines.

    Returns:
        A string with each line prefixed by its number (1-indexed),
        e.g., "1: def hello():\n2:     print('world')"
    """
    if not code_string:
        return ""
    lines = code_string.splitlines()
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered_lines)

def add_line_numbers_to_list(code_lines: list[str]) -> list[str]:
    """
    Adds line numbers to a list of code lines.

    Args:
        code_lines: A list of strings, where each string is a line of code.

    Returns:
        A list of strings with each line prefixed by its number (1-indexed).
    """
    if not code_lines:
        return []
    return [f"{i+1}: {line}" for i, line in enumerate(code_lines)]

# We can add other code utilities here later, such as stripping line numbers
# or basic syntax validation (as mentioned in architecture.md), if needed.
# For now, this fulfills the immediate roadmap item.