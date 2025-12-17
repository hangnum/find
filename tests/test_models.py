"""Unit tests for data models."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.core.models import (
    FileInfo,
    SearchParams,
    SearchQuery,
    SearchResult,
    SizeUnit,
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
        assert query.min_size is None
        assert query.max_size is None
        assert query.modified_after is None
        assert query.modified_before is None
        assert query.content_pattern is None

    def test_with_extensions(self):
        """Test query with file extensions."""
        query = SearchQuery(extensions=[".py", ".txt"])
        assert query.extensions == [".py", ".txt"]

    def test_with_multiple_extensions(self):
        """Test query with many extensions."""
        exts = [".py", ".txt", ".md", ".json", ".yaml"]
        query = SearchQuery(extensions=exts)
        assert len(query.extensions) == 5

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

    def test_with_date_range(self):
        """Test query with date range."""
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()
        query = SearchQuery(modified_after=start, modified_before=end)
        assert query.modified_after == start
        assert query.modified_before == end

    def test_with_content_pattern(self):
        """Test query with content search pattern."""
        query = SearchQuery(content_pattern="TODO")
        assert query.content_pattern == "TODO"

    def test_with_custom_path(self):
        """Test query with custom search path."""
        custom_path = Path("/custom/path")
        query = SearchQuery(path=custom_path)
        assert query.path == custom_path

    def test_non_recursive_search(self):
        """Test non-recursive search option."""
        query = SearchQuery(recursive=False)
        assert query.recursive is False

    def test_include_hidden_files(self):
        """Test include hidden files option."""
        query = SearchQuery(include_hidden=True)
        assert query.include_hidden is True

    def test_combined_filters(self):
        """Test query with multiple filters combined."""
        query = SearchQuery(
            extensions=[".py"],
            min_size=1024,
            include_hidden=True,
            recursive=True,
            pattern="test_*",
        )
        assert query.extensions == [".py"]
        assert query.min_size == 1024
        assert query.include_hidden is True
        assert query.pattern == "test_*"


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

    def test_file_timestamps(self, temp_files: Path):
        """Test file timestamp fields."""
        py_file = temp_files / "test.py"
        info = FileInfo.from_path(py_file)

        assert isinstance(info.created, datetime)
        assert isinstance(info.modified, datetime)
        assert info.created <= info.modified

    def test_file_without_extension(self, temp_files: Path):
        """Test file without extension."""
        no_ext_file = temp_files / "noextension"
        no_ext_file.write_text("content")
        info = FileInfo.from_path(no_ext_file)

        assert info.name == "noextension"
        assert info.extension == ""

    def test_hidden_file(self, temp_files: Path):
        """Test hidden file info."""
        hidden = temp_files / ".hidden"
        info = FileInfo.from_path(hidden)

        assert info.name == ".hidden"
        assert info.name.startswith(".")

    def test_empty_file(self, temp_files: Path):
        """Test empty file size."""
        empty = temp_files / "test.pdf"
        info = FileInfo.from_path(empty)
        assert info.size == 0


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

    def test_sort_by_modified(self):
        """Test sort by modified date."""
        query = SearchQuery()
        params = SearchParams(query=query, sort_by=SortField.MODIFIED)
        assert params.sort_by == SortField.MODIFIED

    def test_sort_by_created(self):
        """Test sort by created date."""
        query = SearchQuery()
        params = SearchParams(query=query, sort_by=SortField.CREATED)
        assert params.sort_by == SortField.CREATED

    def test_small_limit(self):
        """Test small result limit."""
        query = SearchQuery()
        params = SearchParams(query=query, limit=10)
        assert params.limit == 10


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

    def test_result_with_files(self, temp_files: Path):
        """Test result with file list."""
        py_file = temp_files / "test.py"
        file_info = FileInfo.from_path(py_file)

        query = SearchQuery()
        result = SearchResult(
            query=query,
            files=[file_info],
            total_count=1,
            search_time=0.05,
        )

        assert result.total_count == 1
        assert len(result.files) == 1
        assert result.files[0].name == "test.py"

    def test_search_time_recorded(self):
        """Test search time is recorded."""
        query = SearchQuery()
        result = SearchResult(
            query=query,
            files=[],
            total_count=0,
            search_time=1.234,
        )
        assert result.search_time == 1.234

    def test_result_preserves_query(self):
        """Test result preserves original query."""
        query = SearchQuery(extensions=[".py"], min_size=1024)
        result = SearchResult(
            query=query,
            files=[],
            total_count=0,
            search_time=0.1,
        )
        assert result.query.extensions == [".py"]
        assert result.query.min_size == 1024


class TestEnums:
    """Tests for enum types."""

    def test_size_unit_values(self):
        """Test SizeUnit enum values."""
        assert SizeUnit.BYTES.value == "B"
        assert SizeUnit.KB.value == "KB"
        assert SizeUnit.MB.value == "MB"
        assert SizeUnit.GB.value == "GB"

    def test_sort_field_values(self):
        """Test SortField enum values."""
        assert SortField.NAME.value == "name"
        assert SortField.SIZE.value == "size"
        assert SortField.MODIFIED.value == "modified"
        assert SortField.CREATED.value == "created"

    def test_sort_order_values(self):
        """Test SortOrder enum values."""
        assert SortOrder.ASC.value == "asc"
        assert SortOrder.DESC.value == "desc"

