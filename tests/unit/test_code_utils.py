# tests/unit/test_code_utils.py

import pytest

from src.utils.code_utils import add_line_numbers, add_line_numbers_to_list

def test_add_line_numbers_empty_string():
    assert add_line_numbers("") == ""

def test_add_line_numbers_single_line():
    assert add_line_numbers("hello world") == "1: hello world"

def test_add_line_numbers_multiple_lines():
    code = "def foo():\n    return 'bar'"
    expected = "1: def foo():\n2:     return 'bar'"
    assert add_line_numbers(code) == expected

def test_add_line_numbers_with_trailing_newline():
    code = "line1\nline2\n" # splitlines() handles this well
    expected = "1: line1\n2: line2"
    assert add_line_numbers(code) == expected

def test_add_line_numbers_to_list_empty():
    assert add_line_numbers_to_list([]) == []

def test_add_line_numbers_to_list_single_line():
    assert add_line_numbers_to_list(["hello world"]) == ["1: hello world"]

def test_add_line_numbers_to_list_multiple_lines():
    code_list = ["def foo():", "    return 'bar'"]
    expected = ["1: def foo():", "2:     return 'bar'"]
    assert add_line_numbers_to_list(code_list) == expected