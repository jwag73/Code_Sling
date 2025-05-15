# src/core/injector.py
from typing import List
from src.core.parser import ParsedInstruction, InsertInstruction, DeleteInstruction

def apply_instructions(original_code: str, instructions: List[ParsedInstruction]) -> str:
    """
    Applies a list of parsed instructions (inserts and deletes) to the original code.

    Args:
        original_code: The original code as a multi-line string.
        instructions: A list of ParsedInstruction objects.

    Returns:
        The modified code as a multi-line string.
    """
    original_lines = original_code.splitlines()
    num_original_lines = len(original_lines)
    
    # --- Pre-process instructions for easier application ---
    
    # 1. Collect all line numbers to be deleted (1-indexed)
    lines_to_delete = set()
    for instruction in instructions:
        if isinstance(instruction, DeleteInstruction):
            start_line = instruction.line_start
            end_line = instruction.line_end if instruction.line_end is not None else instruction.line_start
            for i in range(start_line, end_line + 1):
                if 1 <= i <= num_original_lines: # Ensure valid line numbers
                    lines_to_delete.add(i)

    # 2. Group insertions by the line number they should appear before (1-indexed)
    insertions_before_line = {} # {line_num: [content1, content2, ...]}
    for instruction in instructions:
        if isinstance(instruction, InsertInstruction):
            line_before = instruction.line_before
            # Ensure line_before is within a reasonable range (1 to num_lines + 1 for appending)
            if not (1 <= line_before <= num_original_lines + 1):
                # Skip or log invalid insertion line numbers
                # print(f"Warning: Invalid insertion line_before={line_before}, skipping.")
                continue

            if line_before not in insertions_before_line:
                insertions_before_line[line_before] = []
            insertions_before_line[line_before].append(instruction.content)
            
    # --- Build the new list of lines ---
    new_code_lines: List[str] = []
    
    for i in range(1, num_original_lines + 1): # Iterate through original line numbers (1-indexed)
        # Add any content scheduled for insertion BEFORE the current original line i
        if i in insertions_before_line:
            for content_to_insert in insertions_before_line[i]:
                new_code_lines.append(content_to_insert)
        
        # If current original line i is NOT marked for deletion, add it
        if i not in lines_to_delete:
            new_code_lines.append(original_lines[i-1]) # original_lines is 0-indexed

    # Handle insertions that are meant to go after all original lines
    # (e.g., if line_before was num_original_lines + 1)
    after_last_line_key = num_original_lines + 1
    if after_last_line_key in insertions_before_line:
        for content_to_insert in insertions_before_line[after_last_line_key]:
            new_code_lines.append(content_to_insert)
            
    return "\n".join(new_code_lines)