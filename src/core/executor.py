"""Search executor for file system operations."""

import fnmatch
import time
from pathlib import Path
from typing import Generator

from loguru import logger

from src.core.exceptions import InvalidPathError, PermissionDeniedError
from src.core.models import FileInfo, SearchParams, SearchQuery, SearchResult


class SearchExecutor:
    """Executor that performs file system searches based on SearchParams.

    This class handles the actual file system traversal and filtering
    based on the parsed search query.
    """

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

        logger.info(f"Searching in: {query.path}")
        logger.debug(f"Query: {query}")

        # Collect matching files
        files: list[FileInfo] = []
        for file_info in self._search_files(query):
            files.append(file_info)
            if len(files) >= params.limit:
                break

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

    def _search_files(self, query: SearchQuery) -> Generator[FileInfo, None, None]:
        """Generate matching files based on query.

        Args:
            query: Search query with filters.

        Yields:
            FileInfo for each matching file.
        """
        try:
            if query.recursive:
                paths = query.path.rglob("*")
            else:
                paths = query.path.glob("*")

            for path in paths:
                if self._matches_query(path, query):
                    try:
                        yield FileInfo.from_path(path)
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Cannot access file {path}: {e}")
                        continue

        except PermissionError as e:
            raise PermissionDeniedError(f"Permission denied: {query.path}") from e

    def _matches_query(self, path: Path, query: SearchQuery) -> bool:
        """Check if a path matches the search query.

        Args:
            path: Path to check.
            query: Search query with filters.

        Returns:
            True if path matches all query criteria.
        """
        # Skip directories unless specifically searching for them
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

        # Check file size
        try:
            stat = path.stat()

            if query.min_size is not None and stat.st_size < query.min_size:
                return False

            if query.max_size is not None and stat.st_size > query.max_size:
                return False

            # Check modification time
            if query.modified_after is not None:
                mtime = stat.st_mtime
                if mtime < query.modified_after.timestamp():
                    return False

            if query.modified_before is not None:
                mtime = stat.st_mtime
                if mtime > query.modified_before.timestamp():
                    return False

        except (OSError, PermissionError):
            return False

        # Check content pattern (expensive - do last)
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
