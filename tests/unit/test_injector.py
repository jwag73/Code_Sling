# tests/unit/test_injector.py
import pytest
from src.core.injector import apply_instructions
from src.core.parser import InsertInstruction, DeleteInstruction

def test_apply_no_instructions():
    code = "line1\nline2\nline3"
    instructions = []
    assert apply_instructions(code, instructions) == code

def test_apply_simple_insert():
    code = "line1\nline3"
    instructions = [InsertInstruction(line_before=2, content="line2_inserted")]
    expected = "line1\nline2_inserted\nline3"
    assert apply_instructions(code, instructions) == expected

def test_apply_insert_at_beginning():
    code = "line2\nline3"
    instructions = [InsertInstruction(line_before=1, content="line1_inserted")]
    expected = "line1_inserted\nline2\nline3"
    assert apply_instructions(code, instructions) == expected

def test_apply_insert_at_end():
    code = "line1\nline2"
    # To insert after last line, line_before should be len(lines) + 1
    instructions = [InsertInstruction(line_before=3, content="line3_inserted")]
    expected = "line1\nline2\nline3_inserted"
    assert apply_instructions(code, instructions) == expected

def test_apply_multiple_inserts_at_same_point():
    code = "line1\nline4"
    instructions = [
        InsertInstruction(line_before=2, content="line2_inserted"),
        InsertInstruction(line_before=2, content="line3_inserted")
    ]
    # Order of multiple insertions at the same point depends on stability if not specified,
    # current implementation adds them in order they appear in instructions list.
    expected = "line1\nline2_inserted\nline3_inserted\nline4"
    assert apply_instructions(code, instructions) == expected

def test_apply_simple_delete():
    code = "line1\nline_to_delete\nline3"
    instructions = [DeleteInstruction(line_start=2)]
    expected = "line1\nline3"
    assert apply_instructions(code, instructions) == expected

def test_apply_delete_range():
    code = "line1\nline2_del\nline3_del\nline4_del\nline5"
    instructions = [DeleteInstruction(line_start=2, line_end=4)]
    expected = "line1\nline5"
    assert apply_instructions(code, instructions) == expected

def test_apply_delete_first_line():
    code = "line1_del\nline2\nline3"
    instructions = [DeleteInstruction(line_start=1)]
    expected = "line2\nline3"
    assert apply_instructions(code, instructions) == expected

def test_apply_delete_last_line():
    code = "line1\nline2\nline3_del"
    instructions = [DeleteInstruction(line_start=3)]
    expected = "line1\nline2"
    assert apply_instructions(code, instructions) == expected

def test_apply_delete_all_lines():
    code = "line1\nline2\nline3"
    instructions = [DeleteInstruction(line_start=1, line_end=3)]
    expected = "" # All lines deleted
    assert apply_instructions(code, instructions) == expected

def test_apply_mixed_insert_and_delete():
    code = "aaa\nbbb\nccc\nddd\neee"
    instructions = [
        DeleteInstruction(line_start=2), # delete 'bbb'
        InsertInstruction(line_before=3, content="new_ccc_before_orig_ccc"), # insert before 'ccc'
        DeleteInstruction(line_start=4, line_end=5) # delete 'ddd', 'eee'
    ]
    # Expected processing:
    # Original lines: aaa, bbb, ccc, ddd, eee
    # 1. Deletions marked: bbb (line 2), ddd (line 4), eee (line 5)
    # 2. Insertions: "new_ccc_before_orig_ccc" before line 3 ('ccc')
    #
    # Iteration:
    # Line 1 ('aaa'): Keep. Output: "aaa"
    # Line 2 ('bbb'): Deleted.
    # Line 3 ('ccc'): Insert "new_ccc_before_orig_ccc". Keep 'ccc'. Output: "aaa", "new_ccc_before_orig_ccc", "ccc"
    # Line 4 ('ddd'): Deleted.
    # Line 5 ('eee'): Deleted.
    expected = "aaa\nnew_ccc_before_orig_ccc\nccc"
    assert apply_instructions(code, instructions) == expected

def test_apply_instructions_out_of_order():
    # Instructions might not be sorted by line number initially
    code = "line1\nline2\nline3\nline4"
    instructions = [
        InsertInstruction(line_before=4, content="inserted_before_4"),
        DeleteInstruction(line_start=1)
    ]
    # Processed:
    # Delete line 1.
    # Insert before original line 4.
    # Lines: line2, line3, inserted_before_4, line4
    expected = "line2\nline3\ninserted_before_4\nline4"
    assert apply_instructions(code, instructions) == expected

def test_apply_delete_invalid_range():
    # line_start/line_end outside bounds should be handled gracefully (ignored by current impl)
    code = "line1\nline2"
    instructions = [DeleteInstruction(line_start=5, line_end=10)]
    assert apply_instructions(code, instructions) == code # No change

def test_apply_insert_invalid_line_before():
    code = "line1\nline2"
    # line_before=0 or line_before > num_lines + 1 should be ignored
    instructions = [
        InsertInstruction(line_before=0, content="invalid1"),
        InsertInstruction(line_before=5, content="invalid2")
    ]
    assert apply_instructions(code, instructions) == code # No change

def test_empty_original_code():
    code = ""
    instructions = [InsertInstruction(line_before=1, content="hello")]
    expected = "hello"
    assert apply_instructions(code, instructions) == expected

def test_empty_original_code_delete_noop():
    code = ""
    instructions = [DeleteInstruction(line_start=1)]
    expected = ""
    assert apply_instructions(code, instructions) == expected