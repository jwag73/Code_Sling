# src/core/parser.py
import re
from dataclasses import dataclass, field
from typing import List, Union, Literal, Optional

# --------------------------------------------------------------------------- #
# Data models
# --------------------------------------------------------------------------- #
@dataclass
class InsertInstruction:
    line_before: int
    content: str
    type: Literal["insert"] = field(default="insert", init=False)


@dataclass
class DeleteInstruction:
    line_start: int
    line_end: Optional[int] = None
    type: Literal["delete"] = field(default="delete", init=False)


ParsedInstruction = Union[InsertInstruction, DeleteInstruction]

# --------------------------------------------------------------------------- #
# Regex patterns
# --------------------------------------------------------------------------- #
# INSERT <line>: <content>
# * allow leading/trailing spaces on the *instruction* line
# * tolerate spaces around the colon
# * drop at most ONE space immediately after the colon (the delimiter)
INSERT_PATTERN = re.compile(
    r"^\s*INSERT\s+(\d+)\s*:\s?(.*)$", re.IGNORECASE
)

# DELETE single line
DELETE_SINGLE_PATTERN = re.compile(
    r"^\s*DELETE\s+(\d+)\s*$", re.IGNORECASE
)

# DELETE range
DELETE_RANGE_PATTERN = re.compile(
    r"^\s*DELETE\s+(\d+)\s*-\s*(\d+)\s*$", re.IGNORECASE
)

# NO CHANGES
NO_CHANGES_PATTERN = re.compile(r"^\s*NO\s+CHANGES\s*$", re.IGNORECASE)

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def parse_instructions(instruction_string: str) -> List[ParsedInstruction]:
    """
    Convert the AI’s instruction block into structured objects.

    * Leading/trailing **blank lines** are ignored.
    * Spaces inside the code content after the colon are preserved exactly.
    """
    if not instruction_string or instruction_string.strip().upper().startswith("ERROR:"):
        return []

    # Quick path for “NO CHANGES”
    if NO_CHANGES_PATTERN.fullmatch(instruction_string.strip()):
        return []

    parsed_ops: List[ParsedInstruction] = []

    # Walk raw lines so we never strip the spaces that belong to code content.
    for line in instruction_string.splitlines():
        if not line.strip():  # skip completely blank lines
            continue

        # DELETE range (more specific than single)
        m = DELETE_RANGE_PATTERN.match(line)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            if start <= end:  # ignore invalid “15-10” style ranges
                parsed_ops.append(DeleteInstruction(line_start=start, line_end=end))
            continue

        # DELETE single
        m = DELETE_SINGLE_PATTERN.match(line)
        if m:
            parsed_ops.append(DeleteInstruction(line_start=int(m.group(1))))
            continue

        # INSERT
        m = INSERT_PATTERN.match(line)
        if m:
            line_before = int(m.group(1))
            content = m.group(2)  # already minus at most one leading space
            parsed_ops.append(InsertInstruction(line_before=line_before, content=content))
            continue

        # Unrecognised line – silently skip (could log a warning)

    return parsed_ops
