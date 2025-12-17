"""Unit tests for search executor."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.core.exceptions import InvalidPathError
from src.core.executor import SearchExecutor
from src.core.models import SearchParams, SearchQuery, SortField, SortOrder


class TestSearchExecutor:
    """Tests for SearchExecutor."""

    def test_search_all_files(self, temp_files: Path):
        """Test searching for all files."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files)
        params = SearchParams(query=query)

        result = executor.execute(params)

        # Should find test.py, test.txt, test.pdf, subdir/nested.py
        # Should NOT find .hidden (hidden file)
        assert result.total_count == 4

    def test_search_by_extension(self, temp_files: Path):
        """Test filtering by file extension."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, extensions=[".py"])
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 2  # test.py and subdir/nested.py
        assert all(f.extension == ".py" for f in result.files)

    def test_search_non_recursive(self, temp_files: Path):
        """Test non-recursive search."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, extensions=[".py"], recursive=False)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 1  # Only test.py, not subdir/nested.py

    def test_search_include_hidden(self, temp_files: Path):
        """Test including hidden files."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, include_hidden=True)
        params = SearchParams(query=query)

        result = executor.execute(params)

        # Should now include .hidden
        assert result.total_count == 5
        hidden_files = [f for f in result.files if f.name.startswith(".")]
        assert len(hidden_files) == 1

    def test_search_by_pattern(self, temp_files: Path):
        """Test filtering by filename pattern."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, pattern="test.*")
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 3  # test.py, test.txt, test.pdf
        assert all(f.name.startswith("test.") for f in result.files)

    def test_search_by_size(self, temp_files: Path, large_file: Path):
        """Test filtering by file size."""
        executor = SearchExecutor()
        # Search for files larger than 500KB
        query = SearchQuery(path=large_file.parent, min_size=500 * 1024)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 1
        assert result.files[0].name == "large.bin"

    def test_search_by_content(self, temp_files: Path):
        """Test content search."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, content_pattern="Hello World")
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 1
        assert result.files[0].name == "test.txt"

    def test_sort_by_name(self, temp_files: Path):
        """Test sorting by name."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, recursive=False)
        params = SearchParams(
            query=query, sort_by=SortField.NAME, sort_order=SortOrder.ASC
        )

        result = executor.execute(params)

        names = [f.name for f in result.files]
        assert names == sorted(names, key=str.lower)

    def test_sort_by_size_desc(self, temp_files: Path):
        """Test sorting by size descending."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, recursive=False)
        params = SearchParams(
            query=query, sort_by=SortField.SIZE, sort_order=SortOrder.DESC
        )

        result = executor.execute(params)

        sizes = [f.size for f in result.files]
        assert sizes == sorted(sizes, reverse=True)

    def test_invalid_path_raises_error(self):
        """Test that invalid path raises InvalidPathError."""
        executor = SearchExecutor()
        query = SearchQuery(path=Path("/nonexistent/path"))
        params = SearchParams(query=query)

        with pytest.raises(InvalidPathError):
            executor.execute(params)

    def test_limit_results(self, temp_files: Path):
        """Test limiting number of results."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files)
        params = SearchParams(query=query, limit=2)

        result = executor.execute(params)

        assert len(result.files) == 2
