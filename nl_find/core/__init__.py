"""Core engine module for NL-Find."""

from nl_find.core.exceptions import (
    ConfigError,
    InvalidConfigError,
    InvalidPathError,
    LLMConnectionError,
    LLMError,
    LLMParseError,
    LLMResponseError,
    MissingAPIKeyError,
    NLFindError,
    PermissionDeniedError,
    SearchError,
)
from nl_find.core.executor import SearchExecutor
from nl_find.core.models import FileInfo, SearchParams, SearchQuery, SearchResult

__all__ = [
    # Models
    "SearchQuery",
    "SearchParams",
    "FileInfo",
    "SearchResult",
    # Executor
    "SearchExecutor",
    # Exceptions
    "NLFindError",
    "LLMError",
    "LLMConnectionError",
    "LLMParseError",
    "LLMResponseError",
    "SearchError",
    "InvalidPathError",
    "PermissionDeniedError",
    "ConfigError",
    "MissingAPIKeyError",
    "InvalidConfigError",
]
