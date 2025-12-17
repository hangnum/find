"""Unit tests for CLI application."""

from pathlib import Path
from unittest.mock import patch

import pytest

from nl_find.cli.app import format_size
from nl_find.core.models import SortField


class TestFormatSize:
    """Tests for format_size helper function."""

    def test_format_bytes(self):
        """Test formatting bytes."""
        assert format_size(100) == "100.0 B"
        assert format_size(0) == "0.0 B"

    def test_format_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(2048) == "2.0 KB"

    def test_format_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_format_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1024**3) == "1.0 GB"

    def test_format_terabytes(self):
        """Test formatting terabytes."""
        assert format_size(1024**4) == "1.0 TB"

    def test_format_petabytes(self):
        """Test formatting petabytes (edge case)."""
        assert format_size(1024**5) == "1.0 PB"


class TestSortFieldParsing:
    """Tests for SortField enum parsing."""

    def test_valid_sort_field_name(self):
        """Test parsing 'name' sort field."""
        assert SortField("name") == SortField.NAME

    def test_valid_sort_field_size(self):
        """Test parsing 'size' sort field."""
        assert SortField("size") == SortField.SIZE

    def test_valid_sort_field_modified(self):
        """Test parsing 'modified' sort field."""
        assert SortField("modified") == SortField.MODIFIED

    def test_valid_sort_field_created(self):
        """Test parsing 'created' sort field."""
        assert SortField("created") == SortField.CREATED

    def test_invalid_sort_field_raises_value_error(self):
        """Test that invalid sort field raises ValueError."""
        with pytest.raises(ValueError):
            SortField("invalid")

    def test_all_sort_fields_have_string_values(self):
        """Test that all sort fields can be created from their values."""
        for field in SortField:
            assert SortField(field.value) == field


class TestSortFieldEnumMembership:
    """Tests for SortField enum membership checking."""

    def test_valid_value_in_members(self):
        """Test that valid sort field values are in __members__."""
        # This is the fix we made - ensure the correct way works
        assert "name" in [f.value for f in SortField]
        assert "size" in [f.value for f in SortField]
        assert "modified" in [f.value for f in SortField]
        assert "created" in [f.value for f in SortField]

    def test_member_lookup_by_name(self):
        """Test that members can be looked up by name."""
        assert SortField.__members__["NAME"] == SortField.NAME
        assert SortField.__members__["SIZE"] == SortField.SIZE
