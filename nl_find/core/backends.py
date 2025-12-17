"""Search backends for file system operations.

This module provides multiple search backend implementations that can be
used by the SearchExecutor. Backends are selected based on availability
and user configuration.
"""

import shutil
import subprocess
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path

from loguru import logger

from nl_find.core.models import SearchQuery


class SearchBackend(ABC):
    """Abstract base class for search backends.

    All search backends must implement this interface to be used by
    the SearchExecutor.
    """

    name: str = "base"

    @abstractmethod
    def search(self, query: SearchQuery) -> Generator[Path, None, None]:
        """Execute search and yield matching file paths.

        Args:
            query: Search query with filters.

        Yields:
            Path objects for each matching file.
        """

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this backend is available on the current system.

        Returns:
            True if the backend can be used.
        """


class PythonBackend(SearchBackend):
    """Pure Python search backend using pathlib.

    This is the fallback backend that works on all platforms without
    external dependencies. It's slower but always available.
    """

    name = "python"

    def search(self, query: SearchQuery) -> Generator[Path, None, None]:
        """Search using Python's pathlib.

        Args:
            query: Search query with filters.

        Yields:
            Path objects for each matching file.
        """

        try:
            if query.recursive:
                paths = query.path.rglob("*")
            else:
                paths = query.path.glob("*")

            for path in paths:
                if self._matches_query(path, query):
                    yield path

        except PermissionError as e:
            logger.warning(f"Permission denied: {e}")

    def _matches_query(self, path: Path, query: SearchQuery) -> bool:
        """Check if a path matches the search query."""
        import fnmatch

        # Skip directories
        if path.is_dir():
            return False

        # Skip hidden files if not included
        if not query.include_hidden and path.name.startswith("."):
            return False

        # Check filename pattern
        if query.pattern and not fnmatch.fnmatch(path.name, query.pattern):
            return False

        # Check extensions
        if query.extensions:
            if path.suffix.lower() not in [ext.lower() for ext in query.extensions]:
                return False

        # Check file size and modification time
        try:
            stat = path.stat()

            if query.min_size is not None and stat.st_size < query.min_size:
                return False

            if query.max_size is not None and stat.st_size > query.max_size:
                return False

            if query.modified_after is not None:
                if stat.st_mtime < query.modified_after.timestamp():
                    return False

            if query.modified_before is not None:
                if stat.st_mtime > query.modified_before.timestamp():
                    return False

        except (OSError, PermissionError):
            return False

        return True

    @classmethod
    def is_available(cls) -> bool:
        """Python backend is always available."""
        return True


class FdBackend(SearchBackend):
    """Search backend using fd (fast find alternative).

    fd is a fast, user-friendly alternative to find written in Rust.
    https://github.com/sharkdp/fd

    Install:
        Windows: winget install sharkdp.fd
        Linux: apt install fd-find / brew install fd
    """

    name = "fd"

    def __init__(self, fd_path: str | None = None):
        """Initialize fd backend.

        Args:
            fd_path: Custom path to fd executable.
        """
        self.fd_path = fd_path or self._find_fd()

    @staticmethod
    def _find_fd() -> str:
        """Find fd executable path."""
        # Try common names
        for name in ["fd", "fd.exe", "fdfind"]:
            path = shutil.which(name)
            if path:
                return path
        return "fd"

    def search(self, query: SearchQuery) -> Generator[Path, None, None]:
        """Search using fd command.

        Args:
            query: Search query with filters.

        Yields:
            Path objects for each matching file.
        """
        cmd = self._build_command(query)
        logger.debug(f"Running fd command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(query.path),
                timeout=300,  # 5 minute timeout
            )

            for line in result.stdout.strip().split("\n"):
                if line:
                    yield query.path / line

        except subprocess.TimeoutExpired:
            logger.error("fd search timed out")
        except subprocess.SubprocessError as e:
            logger.error(f"fd search failed: {e}")

    def _build_command(self, query: SearchQuery) -> list[str]:
        """Build fd command from query.

        Args:
            query: Search query.

        Returns:
            Command as list of strings.
        """
        cmd = [self.fd_path, "--type", "f"]

        # Hidden files
        if query.include_hidden:
            cmd.append("--hidden")

        # Non-recursive
        if not query.recursive:
            cmd.extend(["--max-depth", "1"])

        # Extensions
        for ext in query.extensions:
            ext_clean = ext.lstrip(".")
            cmd.extend(["--extension", ext_clean])

        # Size filters
        if query.min_size is not None:
            cmd.extend(["--size", f"+{query.min_size}b"])
        if query.max_size is not None:
            cmd.extend(["--size", f"-{query.max_size}b"])

        # Pattern (or match all)
        if query.pattern:
            cmd.append(query.pattern)
        else:
            cmd.append(".")

        return cmd

    @classmethod
    def is_available(cls) -> bool:
        """Check if fd is installed."""
        for name in ["fd", "fd.exe", "fdfind"]:
            if shutil.which(name):
                return True
        return False


class FindBackend(SearchBackend):
    """Search backend using Unix find command.

    Works on Linux and macOS. Uses the system's native find command.
    """

    name = "find"

    def search(self, query: SearchQuery) -> Generator[Path, None, None]:
        """Search using find command.

        Args:
            query: Search query with filters.

        Yields:
            Path objects for each matching file.
        """
        cmd = self._build_command(query)
        logger.debug(f"Running find command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            for line in result.stdout.strip().split("\n"):
                if line:
                    yield Path(line)

        except subprocess.TimeoutExpired:
            logger.error("find search timed out")
        except subprocess.SubprocessError as e:
            logger.error(f"find search failed: {e}")

    def _build_command(self, query: SearchQuery) -> list[str]:
        """Build find command from query.

        Args:
            query: Search query.

        Returns:
            Command as list of strings.
        """
        cmd = ["find", str(query.path)]

        # Non-recursive
        if not query.recursive:
            cmd.extend(["-maxdepth", "1"])

        # File type
        cmd.extend(["-type", "f"])

        # Pattern
        if query.pattern:
            cmd.extend(["-name", query.pattern])

        # Extensions (using -o for OR)
        if query.extensions:
            cmd.append("(")
            for i, ext in enumerate(query.extensions):
                if i > 0:
                    cmd.append("-o")
                cmd.extend(["-name", f"*{ext}"])
            cmd.append(")")

        # Size filters
        if query.min_size is not None:
            size_k = query.min_size // 1024 or 1
            cmd.extend(["-size", f"+{size_k}k"])
        if query.max_size is not None:
            size_k = query.max_size // 1024
            cmd.extend(["-size", f"-{size_k}k"])

        # Time filters
        if query.modified_after is not None:
            from datetime import datetime
            days = (datetime.now() - query.modified_after).days
            if days >= 0:
                cmd.extend(["-mtime", f"-{days}"])

        return cmd

    @classmethod
    def is_available(cls) -> bool:
        """Check if find is available (Unix systems)."""
        import platform
        if platform.system() == "Windows":
            return False
        return shutil.which("find") is not None


class EverythingBackend(SearchBackend):
    """Search backend using Everything (Windows only).

    Everything is an ultra-fast file search engine for Windows that uses
    NTFS indexing for instant results.
    https://www.voidtools.com/

    Requires Everything to be installed and running, plus the command-line
    interface (es.exe).
    """

    name = "everything"

    def __init__(self, es_path: str | None = None):
        """Initialize Everything backend.

        Args:
            es_path: Custom path to es.exe (Everything CLI).
        """
        self.es_path = es_path or self._find_es()

    @staticmethod
    def _find_es() -> str:
        """Find es.exe path."""
        path = shutil.which("es")
        if path:
            return path
        # Common installation paths
        common_paths = [
            r"C:\Program Files\Everything\es.exe",
            r"C:\Program Files (x86)\Everything\es.exe",
        ]
        for p in common_paths:
            if Path(p).exists():
                return p
        return "es"

    def search(self, query: SearchQuery) -> Generator[Path, None, None]:
        """Search using Everything CLI.

        Args:
            query: Search query with filters.

        Yields:
            Path objects for each matching file.
        """
        cmd = self._build_command(query)
        logger.debug(f"Running Everything command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            for line in result.stdout.strip().split("\n"):
                if line:
                    path = Path(line)
                    # Filter by query.path since Everything searches globally
                    if str(path).startswith(str(query.path)):
                        yield path

        except subprocess.TimeoutExpired:
            logger.error("Everything search timed out")
        except subprocess.SubprocessError as e:
            logger.error(f"Everything search failed: {e}")

    def _build_command(self, query: SearchQuery) -> list[str]:
        """Build Everything CLI command from query.

        Args:
            query: Search query.

        Returns:
            Command as list of strings.
        """
        cmd = [self.es_path]

        # Search within path
        search_terms = [f'path:"{query.path}"']

        # Extensions
        if query.extensions:
            ext_pattern = "|".join(ext.lstrip(".") for ext in query.extensions)
            search_terms.append(f"ext:{ext_pattern}")

        # Pattern
        if query.pattern:
            search_terms.append(query.pattern)

        # Size filters
        if query.min_size is not None:
            cmd.extend(["-size-min", str(query.min_size)])
        if query.max_size is not None:
            cmd.extend(["-size-max", str(query.max_size)])

        cmd.append(" ".join(search_terms))
        return cmd

    @classmethod
    def is_available(cls) -> bool:
        """Check if Everything CLI is available."""
        import platform
        if platform.system() != "Windows":
            return False

        # Check for es.exe
        if shutil.which("es"):
            return True

        common_paths = [
            r"C:\Program Files\Everything\es.exe",
            r"C:\Program Files (x86)\Everything\es.exe",
        ]
        return any(Path(p).exists() for p in common_paths)


# Backend registry for easy lookup
BACKENDS: dict[str, type[SearchBackend]] = {
    "python": PythonBackend,
    "fd": FdBackend,
    "find": FindBackend,
    "everything": EverythingBackend,
}


def get_available_backends() -> list[type[SearchBackend]]:
    """Get list of available backends in priority order.

    Returns:
        List of available backend classes.
    """
    priority = [FdBackend, EverythingBackend, FindBackend, PythonBackend]
    return [b for b in priority if b.is_available()]


def select_backend(preference: str = "auto") -> SearchBackend:
    """Select and instantiate the best available backend.

    Args:
        preference: Backend preference ('auto', 'fd', 'find', 'everything', 'python').

    Returns:
        Instantiated search backend.
    """
    if preference != "auto" and preference in BACKENDS:
        backend_cls = BACKENDS[preference]
        if backend_cls.is_available():
            logger.info(f"Using requested backend: {preference}")
            return backend_cls()
        logger.warning(f"Requested backend '{preference}' not available, using auto")

    available = get_available_backends()
    if available:
        backend = available[0]()
        logger.info(f"Auto-selected backend: {backend.name}")
        return backend

    # Should never happen since PythonBackend is always available
    return PythonBackend()
