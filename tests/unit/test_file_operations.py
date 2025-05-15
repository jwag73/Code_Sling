# tests/unit/test_file_operations.py
import pytest
from pathlib import Path
from src.utils.file_operations import read_file, write_file

def test_read_file_success(tmp_path: Path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("Hello World")
    assert read_file(str(p)) == "Hello World"

def test_read_file_not_found():
    with pytest.raises(FileNotFoundError, match="Error: File not found at non_existent_file.txt"):
        read_file("non_existent_file.txt")

def test_write_file_success(tmp_path: Path):
    p = tmp_path / "output.txt"
    content = "This is test content.\nWith multiple lines."
    write_file(str(p), content)
    assert p.read_text(encoding="utf-8") == content

# Optional: Test write_file error (e.g., permission denied), harder to test reliably in all environments.