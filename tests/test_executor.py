"""Unit tests for search executor."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from nl_find.core.exceptions import InvalidPathError
from nl_find.core.executor import SearchExecutor
from nl_find.core.models import SearchParams, SearchQuery, SortField, SortOrder


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

    def test_search_multiple_extensions(self, temp_files: Path):
        """Test filtering by multiple extensions."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, extensions=[".py", ".txt"])
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 3  # test.py, test.txt, subdir/nested.py
        assert all(f.extension in [".py", ".txt"] for f in result.files)

    def test_search_case_insensitive_extension(self, temp_files: Path):
        """Test extension matching is case-insensitive."""
        # Create a file with uppercase extension (different name to avoid collision on Windows)
        upper_file = temp_files / "upper.PY"
        upper_file.write_text("# Python with uppercase extension")

        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, extensions=[".py"])
        params = SearchParams(query=query)

        result = executor.execute(params)

        # Should find test.py, upper.PY, and subdir/nested.py
        assert result.total_count == 3

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

    def test_search_pattern_with_wildcard(self, temp_files: Path):
        """Test pattern with middle wildcard."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, pattern="*.py")
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert all(f.name.endswith(".py") for f in result.files)

    def test_search_by_min_size(self, temp_files: Path, large_file: Path):
        """Test filtering by minimum file size."""
        executor = SearchExecutor()
        # Search for files larger than 500KB
        query = SearchQuery(path=large_file.parent, min_size=500 * 1024)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 1
        assert result.files[0].name == "large.bin"

    def test_search_by_max_size(self, temp_files: Path):
        """Test filtering by maximum file size."""
        executor = SearchExecutor()
        # Search for files smaller than 100 bytes
        query = SearchQuery(path=temp_files, max_size=100)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert all(f.size <= 100 for f in result.files)

    def test_search_by_size_range(self, temp_files: Path):
        """Test filtering by size range."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, min_size=10, max_size=500)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert all(10 <= f.size <= 500 for f in result.files)

    def test_search_by_content(self, temp_files: Path):
        """Test content search."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, content_pattern="Hello World")
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 1
        assert result.files[0].name == "test.txt"

    def test_search_by_content_case_insensitive(self, temp_files: Path):
        """Test content search is case-insensitive."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, content_pattern="hello world")
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 1
        assert result.files[0].name == "test.txt"

    def test_search_by_modified_after(self, temp_files: Path):
        """Test filtering by modification date (after)."""
        # All test files were just created, so they should be recent
        yesterday = datetime.now() - timedelta(days=1)
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, modified_after=yesterday)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count > 0

    def test_search_by_modified_before(self, temp_files: Path):
        """Test filtering by modification date (before)."""
        # All test files were just created, so future date should include all
        tomorrow = datetime.now() + timedelta(days=1)
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, modified_before=tomorrow)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 4

    def test_search_by_date_range(self, temp_files: Path):
        """Test filtering by date range."""
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)
        executor = SearchExecutor()
        query = SearchQuery(
            path=temp_files, modified_after=yesterday, modified_before=tomorrow
        )
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count > 0

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

    def test_sort_by_name_desc(self, temp_files: Path):
        """Test sorting by name descending."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, recursive=False)
        params = SearchParams(
            query=query, sort_by=SortField.NAME, sort_order=SortOrder.DESC
        )

        result = executor.execute(params)

        names = [f.name for f in result.files]
        assert names == sorted(names, key=str.lower, reverse=True)

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

    def test_sort_by_size_asc(self, temp_files: Path):
        """Test sorting by size ascending."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, recursive=False)
        params = SearchParams(
            query=query, sort_by=SortField.SIZE, sort_order=SortOrder.ASC
        )

        result = executor.execute(params)

        sizes = [f.size for f in result.files]
        assert sizes == sorted(sizes)

    def test_sort_by_modified(self, temp_files: Path):
        """Test sorting by modified date."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files, recursive=False)
        params = SearchParams(
            query=query, sort_by=SortField.MODIFIED, sort_order=SortOrder.DESC
        )

        result = executor.execute(params)

        dates = [f.modified for f in result.files]
        assert dates == sorted(dates, reverse=True)

    def test_invalid_path_raises_error(self):
        """Test that invalid path raises InvalidPathError."""
        executor = SearchExecutor()
        query = SearchQuery(path=Path("/nonexistent/path"))
        params = SearchParams(query=query)

        with pytest.raises(InvalidPathError):
            executor.execute(params)

    def test_file_path_raises_error(self, temp_files: Path):
        """Test that file path (not directory) raises error."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files / "test.py")
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

    def test_limit_one_result(self, temp_files: Path):
        """Test limiting to single result."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files)
        params = SearchParams(query=query, limit=1)

        result = executor.execute(params)

        assert len(result.files) == 1

    def test_search_time_recorded(self, temp_files: Path):
        """Test that search time is recorded."""
        executor = SearchExecutor()
        query = SearchQuery(path=temp_files)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.search_time >= 0

    def test_empty_directory(self, tmp_path: Path):
        """Test searching empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        executor = SearchExecutor()
        query = SearchQuery(path=empty_dir)
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 0

    def test_combined_filters(self, temp_files: Path):
        """Test multiple filters combined."""
        executor = SearchExecutor()
        query = SearchQuery(
            path=temp_files,
            extensions=[".py"],
            recursive=True,
            pattern="*.py",
        )
        params = SearchParams(query=query)

        result = executor.execute(params)

        assert result.total_count == 2
        assert all(f.extension == ".py" for f in result.files)

