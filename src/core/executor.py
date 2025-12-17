"""Search executor for file system operations."""

import fnmatch
import time
from pathlib import Path
from typing import Generator, Optional

from loguru import logger

from src.config.settings import get_settings
from src.core.backends import (
    PythonBackend,
    SearchBackend,
    select_backend,
)
from src.core.exceptions import InvalidPathError, PermissionDeniedError
from src.core.models import FileInfo, SearchParams, SearchQuery, SearchResult


class SearchExecutor:
    """Executor that performs file system searches based on SearchParams.

    This class handles the actual file system traversal and filtering
    based on the parsed search query. It uses a pluggable backend system
    to leverage system-level search tools when available.

    Attributes:
        backend: The search backend being used.
    """

    def __init__(self, backend: Optional[SearchBackend] = None):
        """Initialize the search executor.

        Args:
            backend: Optional search backend. If None, auto-selects best available.
        """
        settings = get_settings()
        backend_preference = settings.search.backend
        self.backend = backend or select_backend(backend_preference)
        logger.info(f"SearchExecutor using backend: {self.backend.name}")

    def execute(self, params: SearchParams) -> SearchResult:
        """Execute a search and return results.

        Args:
            params: Search parameters including query and sort options.

        Returns:
            SearchResult containing matched files.

        Raises:
            InvalidPathError: If the search path doesn't exist.
            PermissionDeniedError: If access to path is denied.
        """
        start_time = time.time()
        query = params.query

        # Validate path
        if not query.path.exists():
            raise InvalidPathError(f"Path does not exist: {query.path}")

        if not query.path.is_dir():
            raise InvalidPathError(f"Path is not a directory: {query.path}")

        logger.info(f"Searching in: {query.path} (backend: {self.backend.name})")
        logger.debug(f"Query: {query}")

        # Collect matching files using the backend
        files: list[FileInfo] = []
        for path in self.backend.search(query):
            try:
                # Apply additional filters not handled by backend
                if self._post_filter(path, query):
                    file_info = FileInfo.from_path(path)
                    files.append(file_info)
                    if len(files) >= params.limit:
                        break
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot access file {path}: {e}")
                continue

        # Sort results
        files = self._sort_files(files, params)

        search_time = time.time() - start_time
        logger.info(f"Found {len(files)} files in {search_time:.2f}s")

        return SearchResult(
            query=query,
            files=files,
            total_count=len(files),
            search_time=search_time,
        )

    def _post_filter(self, path: Path, query: SearchQuery) -> bool:
        """Apply filters that backends may not fully support.

        Args:
            path: Path to check.
            query: Search query with filters.

        Returns:
            True if path passes all filters.
        """
        # Content pattern search (expensive, must be done in Python)
        if query.content_pattern:
            if not self._content_matches(path, query.content_pattern):
                return False

        return True

    def _content_matches(self, path: Path, pattern: str) -> bool:
        """Check if file content matches the pattern.

        Args:
            path: Path to the file.
            pattern: Pattern to search for in content.

        Returns:
            True if pattern is found in file content.
        """
        try:
            # Only search text files
            content = path.read_text(encoding="utf-8", errors="ignore")
            return pattern.lower() in content.lower()
        except (OSError, PermissionError, UnicodeDecodeError):
            return False

    def _sort_files(
        self, files: list[FileInfo], params: SearchParams
    ) -> list[FileInfo]:
        """Sort files based on parameters.

        Args:
            files: List of files to sort.
            params: Search parameters with sort options.

        Returns:
            Sorted list of files.
        """
        reverse = params.sort_order.value == "desc"

        key_map = {
            "name": lambda f: f.name.lower(),
            "size": lambda f: f.size,
            "modified": lambda f: f.modified,
            "created": lambda f: f.created,
        }

        key_func = key_map.get(params.sort_by.value, key_map["name"])
        return sorted(files, key=key_func, reverse=reverse)

