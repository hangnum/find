"""Unit tests for search backends."""

import os
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.backends import (
    BACKENDS,
    EverythingBackend,
    FdBackend,
    FindBackend,
    PythonBackend,
    SearchBackend,
    get_available_backends,
    select_backend,
)
from src.core.models import SearchQuery


class TestPythonBackend:
    """Tests for PythonBackend."""

    def test_is_always_available(self):
        """PythonBackend should always be available."""
        assert PythonBackend.is_available() is True

    def test_search_returns_files(self, temp_directory):
        """Test that search returns matching files."""
        backend = PythonBackend()
        query = SearchQuery(path=temp_directory, recursive=True)

        results = list(backend.search(query))

        assert len(results) > 0
        assert all(isinstance(p, Path) for p in results)

    def test_search_filters_by_extension(self, temp_directory):
        """Test extension filtering."""
        backend = PythonBackend()
        query = SearchQuery(
            path=temp_directory,
            extensions=[".py"],
            recursive=True,
        )

        results = list(backend.search(query))

        assert all(p.suffix == ".py" for p in results)

    def test_search_filters_by_pattern(self, temp_directory):
        """Test pattern filtering."""
        backend = PythonBackend()
        query = SearchQuery(
            path=temp_directory,
            pattern="*.txt",
            recursive=True,
        )

        results = list(backend.search(query))

        assert all(p.suffix == ".txt" for p in results)


class TestFdBackend:
    """Tests for FdBackend."""

    def test_is_available_checks_fd(self):
        """Test fd availability check."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/fd"
            assert FdBackend.is_available() is True

            mock_which.return_value = None
            assert FdBackend.is_available() is False

    def test_build_command_basic(self):
        """Test basic command building."""
        backend = FdBackend(fd_path="fd")
        query = SearchQuery(path=Path("/test"), recursive=True)

        cmd = backend._build_command(query)

        assert cmd[0] == "fd"
        assert "--type" in cmd
        assert "f" in cmd

    def test_build_command_with_extensions(self):
        """Test command building with extensions."""
        backend = FdBackend(fd_path="fd")
        query = SearchQuery(
            path=Path("/test"),
            extensions=[".py", ".txt"],
            recursive=True,
        )

        cmd = backend._build_command(query)

        assert "--extension" in cmd
        assert "py" in cmd
        assert "txt" in cmd

    def test_build_command_with_size(self):
        """Test command building with size filter."""
        backend = FdBackend(fd_path="fd")
        query = SearchQuery(
            path=Path("/test"),
            min_size=1024,
            recursive=True,
        )

        cmd = backend._build_command(query)

        assert "--size" in cmd
        assert "+1024b" in cmd

    def test_build_command_hidden_files(self):
        """Test hidden files flag."""
        backend = FdBackend(fd_path="fd")
        query = SearchQuery(
            path=Path("/test"),
            include_hidden=True,
            recursive=True,
        )

        cmd = backend._build_command(query)

        assert "--hidden" in cmd


class TestFindBackend:
    """Tests for FindBackend (Unix only)."""

    def test_is_available_on_unix(self):
        """Test find availability on Unix."""
        with patch("platform.system") as mock_system:
            with patch("shutil.which") as mock_which:
                mock_system.return_value = "Linux"
                mock_which.return_value = "/usr/bin/find"
                assert FindBackend.is_available() is True

                mock_system.return_value = "Windows"
                assert FindBackend.is_available() is False

    def test_build_command_basic(self):
        """Test basic find command building."""
        backend = FindBackend()
        test_path = Path("/test")
        query = SearchQuery(path=test_path, recursive=True)

        cmd = backend._build_command(query)

        assert cmd[0] == "find"
        assert str(test_path) in cmd
        assert "-type" in cmd
        assert "f" in cmd

    def test_build_command_non_recursive(self):
        """Test non-recursive find command."""
        backend = FindBackend()
        query = SearchQuery(path=Path("/test"), recursive=False)

        cmd = backend._build_command(query)

        assert "-maxdepth" in cmd
        assert "1" in cmd


class TestEverythingBackend:
    """Tests for EverythingBackend (Windows only)."""

    def test_is_available_on_windows(self):
        """Test Everything availability on Windows."""
        with patch("platform.system") as mock_system:
            mock_system.return_value = "Linux"
            assert EverythingBackend.is_available() is False

    def test_build_command_basic(self):
        """Test basic Everything command building."""
        backend = EverythingBackend(es_path="es")
        query = SearchQuery(path=Path("D:/test"), recursive=True)

        cmd = backend._build_command(query)

        assert cmd[0] == "es"
        assert any("path:" in str(arg) for arg in cmd)


class TestBackendSelection:
    """Tests for backend selection logic."""

    def test_backends_registry(self):
        """Test that all backends are registered."""
        assert "python" in BACKENDS
        assert "fd" in BACKENDS
        assert "find" in BACKENDS
        assert "everything" in BACKENDS

    def test_get_available_backends_includes_python(self):
        """PythonBackend should always be in available list."""
        available = get_available_backends()
        assert any(b == PythonBackend for b in available)

    def test_select_backend_auto(self):
        """Test auto backend selection."""
        backend = select_backend("auto")
        assert isinstance(backend, SearchBackend)

    def test_select_backend_python(self):
        """Test explicit Python backend selection."""
        backend = select_backend("python")
        assert isinstance(backend, PythonBackend)

    def test_select_backend_fallback(self):
        """Test fallback when requested backend unavailable."""
        # Request a backend that's likely unavailable
        backend = select_backend("everything")
        # Should get something (either Everything or fallback)
        assert isinstance(backend, SearchBackend)
