"""Data models for NL-Find search queries and results."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class SizeUnit(str, Enum):
    """File size unit."""

    BYTES = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"


class SortField(str, Enum):
    """Sort field for search results."""

    NAME = "name"
    SIZE = "size"
    MODIFIED = "modified"
    CREATED = "created"


class SortOrder(str, Enum):
    """Sort order."""

    ASC = "asc"
    DESC = "desc"


class SearchQuery(BaseModel):
    """Structured search query parsed from natural language.

    Attributes:
        path: Base directory to search in.
        pattern: Filename pattern (glob style).
        extensions: List of file extensions to filter (e.g., [".py", ".txt"]).
        min_size: Minimum file size in bytes.
        max_size: Maximum file size in bytes.
        modified_after: Files modified after this datetime.
        modified_before: Files modified before this datetime.
        content_pattern: Pattern to search within file content.
        include_hidden: Whether to include hidden files.
        recursive: Whether to search recursively.
    """

    path: Path = Field(default_factory=Path.cwd)
    pattern: Optional[str] = None
    extensions: list[str] = Field(default_factory=list)
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    content_pattern: Optional[str] = None
    include_hidden: bool = False
    recursive: bool = True


class SearchParams(BaseModel):
    """Parameters for executing a search.

    Attributes:
        query: The parsed search query.
        sort_by: Field to sort results by.
        sort_order: Sort order (ascending or descending).
        limit: Maximum number of results to return.
    """

    query: SearchQuery
    sort_by: SortField = SortField.NAME
    sort_order: SortOrder = SortOrder.ASC
    limit: int = 1000


class FileInfo(BaseModel):
    """Information about a single file.

    Attributes:
        path: Absolute path to the file.
        name: Filename.
        extension: File extension.
        size: File size in bytes.
        created: Creation timestamp.
        modified: Last modification timestamp.
        is_dir: Whether this is a directory.
    """

    path: Path
    name: str
    extension: str
    size: int
    created: datetime
    modified: datetime
    is_dir: bool = False

    @classmethod
    def from_path(cls, path: Path) -> "FileInfo":
        """Create FileInfo from a Path object.

        Args:
            path: Path to the file.

        Returns:
            FileInfo instance with file metadata.
        """
        stat = path.stat()
        return cls(
            path=path.resolve(),
            name=path.name,
            extension=path.suffix,
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime),
            is_dir=path.is_dir(),
        )


class SearchResult(BaseModel):
    """Search result containing matched files.

    Attributes:
        query: The original search query.
        files: List of matched files.
        total_count: Total number of files found.
        search_time: Time taken to execute search in seconds.
    """

    query: SearchQuery
    files: list[FileInfo]
    total_count: int
    search_time: float
