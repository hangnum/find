"""Pytest fixtures for NL-Find tests."""

from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_files(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory with sample files for testing.

    Creates:
        - test.py (100 bytes)
        - test.txt (50 bytes)
        - test.pdf (empty)
        - subdir/nested.py (30 bytes)
        - .hidden (hidden file)

    Yields:
        Path to the temporary directory.
    """
    # Create regular files
    py_file = tmp_path / "test.py"
    py_file.write_text("# Python file\n" + "x = 1\n" * 20)

    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Hello World\n" * 5)

    pdf_file = tmp_path / "test.pdf"
    pdf_file.touch()

    # Create subdirectory with nested file
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    nested_py = subdir / "nested.py"
    nested_py.write_text("# Nested file\n")

    # Create hidden file
    hidden = tmp_path / ".hidden"
    hidden.write_text("hidden content")

    yield tmp_path


@pytest.fixture
def large_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a large file (1MB) for size testing.

    Yields:
        Path to the large file.
    """
    large = tmp_path / "large.bin"
    large.write_bytes(b"x" * (1024 * 1024))  # 1MB
    yield large
