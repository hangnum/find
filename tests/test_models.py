"""Unit tests for data models."""

from datetime import datetime
from pathlib import Path

import pytest

from src.core.models import (
    FileInfo,
    SearchParams,
    SearchQuery,
    SearchResult,
    SortField,
    SortOrder,
)


class TestSearchQuery:
    """Tests for SearchQuery model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        query = SearchQuery()
        assert query.path == Path.cwd()
        assert query.pattern is None
        assert query.extensions == []
        assert query.recursive is True
        assert query.include_hidden is False

    def test_with_extensions(self):
        """Test query with file extensions."""
        query = SearchQuery(extensions=[".py", ".txt"])
        assert query.extensions == [".py", ".txt"]

    def test_with_size_filters(self):
        """Test query with size filters."""
        query = SearchQuery(min_size=1024, max_size=1048576)
        assert query.min_size == 1024
        assert query.max_size == 1048576

    def test_with_date_filters(self):
        """Test query with date filters."""
        now = datetime.now()
        query = SearchQuery(modified_after=now)
        assert query.modified_after == now


class TestFileInfo:
    """Tests for FileInfo model."""

    def test_from_path(self, temp_files: Path):
        """Test creating FileInfo from a path."""
        py_file = temp_files / "test.py"
        info = FileInfo.from_path(py_file)

        assert info.name == "test.py"
        assert info.extension == ".py"
        assert info.size > 0
        assert info.is_dir is False
        assert info.path == py_file.resolve()

    def test_from_directory(self, temp_files: Path):
        """Test creating FileInfo from a directory."""
        subdir = temp_files / "subdir"
        info = FileInfo.from_path(subdir)

        assert info.name == "subdir"
        assert info.is_dir is True


class TestSearchParams:
    """Tests for SearchParams model."""

    def test_default_sort(self):
        """Test default sort options."""
        query = SearchQuery()
        params = SearchParams(query=query)

        assert params.sort_by == SortField.NAME
        assert params.sort_order == SortOrder.ASC
        assert params.limit == 1000

    def test_custom_sort(self):
        """Test custom sort options."""
        query = SearchQuery()
        params = SearchParams(
            query=query,
            sort_by=SortField.SIZE,
            sort_order=SortOrder.DESC,
            limit=100,
        )

        assert params.sort_by == SortField.SIZE
        assert params.sort_order == SortOrder.DESC
        assert params.limit == 100


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_empty_result(self):
        """Test empty search result."""
        query = SearchQuery()
        result = SearchResult(
            query=query,
            files=[],
            total_count=0,
            search_time=0.1,
        )

        assert result.total_count == 0
        assert len(result.files) == 0
