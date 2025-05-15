# tests/unit/test_parser.py
import pytest

from src.core.parser import (
    parse_instructions,
    InsertInstruction,
    DeleteInstruction
)

def test_parse_empty_string():
    assert parse_instructions("") == []

def test_parse_no_changes():
    assert parse_instructions("NO CHANGES") == []
    assert parse_instructions("no changes") == [] # Test case insensitivity

def test_parse_error_string():
    assert parse_instructions("ERROR: Something went wrong") == []

def test_parse_insert_single_line():
    instructions = "INSERT 1: print('hello')"
    result = parse_instructions(instructions)
    assert len(result) == 1
    assert isinstance(result[0], InsertInstruction)
    assert result[0].line_before == 1
    assert result[0].content == "print('hello')"
    assert result[0].type == "insert"

def test_parse_insert_line_with_leading_spaces_in_content():
    instructions = "INSERT 3:     indented_code()"
    result = parse_instructions(instructions)
    assert len(result) == 1
    assert isinstance(result[0], InsertInstruction)
    assert result[0].line_before == 3
    assert result[0].content == "    indented_code()"

def test_parse_delete_single_line():
    instructions = "DELETE 5"
    result = parse_instructions(instructions)
    assert len(result) == 1
    assert isinstance(result[0], DeleteInstruction)
    assert result[0].line_start == 5
    assert result[0].line_end is None
    assert result[0].type == "delete"

def test_parse_delete_range():
    instructions = "DELETE 10-12"
    result = parse_instructions(instructions)
    assert len(result) == 1
    assert isinstance(result[0], DeleteInstruction)
    assert result[0].line_start == 10
    assert result[0].line_end == 12

def test_parse_delete_invalid_range_skipped():
    instructions = "DELETE 15-10" # Start > End
    result = parse_instructions(instructions)
    assert len(result) == 0 # Or handle as error, current skips

def test_parse_multiple_instructions():
    instructions = """
    INSERT 1: first line
    DELETE 3
    INSERT 5: another line with content
    DELETE 7-9
    """
    result = parse_instructions(instructions)
    assert len(result) == 4
    assert isinstance(result[0], InsertInstruction)
    assert result[0].line_before == 1
    assert result[0].content == "first line"

    assert isinstance(result[1], DeleteInstruction)
    assert result[1].line_start == 3
    assert result[1].line_end is None

    assert isinstance(result[2], InsertInstruction)
    assert result[2].line_before == 5
    assert result[2].content == "another line with content"

    assert isinstance(result[3], DeleteInstruction)
    assert result[3].line_start == 7
    assert result[3].line_end == 9

def test_parse_mixed_case_instructions():
    instructions = "insert 2: mixed case insert\ndeLeTe 4"
    result = parse_instructions(instructions)
    assert len(result) == 2
    assert isinstance(result[0], InsertInstruction)
    assert result[0].line_before == 2
    assert isinstance(result[1], DeleteInstruction)
    assert result[1].line_start == 4

def test_parse_instruction_with_extra_spaces():
    instructions = "  INSERT   22  :  spaced out content  "
    result = parse_instructions(instructions)
    assert len(result) == 1
    assert isinstance(result[0], InsertInstruction)
    assert result[0].line_before == 22
    assert result[0].content == " spaced out content  " # Regex `(.*)` captures spaces

def test_parse_unparseable_line_skipped():
    instructions = "INVALID INSTRUCTION\nINSERT 1: valid"
    result = parse_instructions(instructions)
    assert len(result) == 1 # Only the valid instruction is parsed
    assert isinstance(result[0], InsertInstruction)

def test_parse_instruction_with_empty_content_for_insert():
    # Current AI prompt asks for <exact_code_content>, implying non-empty,
    # but regex (.*) allows empty.
    instructions = "INSERT 10: "
    result = parse_instructions(instructions)
    assert len(result) == 1
    assert isinstance(result[0], InsertInstruction)
    assert result[0].line_before == 10
    assert result[0].content == ""