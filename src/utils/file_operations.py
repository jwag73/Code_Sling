# src/utils/file_operations.py
from pathlib import Path

def read_file(filepath: str) -> str:
    """Reads the content of a file."""
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at {filepath}")
    except Exception as e:
        raise Exception(f"Error reading file {filepath}: {e}")

def write_file(filepath: str, content: str) -> None:
    """Writes content to a file."""
    try:
        Path(filepath).write_text(content, encoding="utf-8")
    except Exception as e:
        raise Exception(f"Error writing file {filepath}: {e}")