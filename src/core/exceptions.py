"""Custom exceptions for NL-Find."""


class NLFindError(Exception):
    """Base exception for NL-Find."""

    pass


class LLMError(NLFindError):
    """Base exception for LLM-related errors."""

    pass


class LLMConnectionError(LLMError):
    """Raised when connection to LLM service fails."""

    pass


class LLMParseError(LLMError):
    """Raised when LLM fails to parse the query."""

    pass


class LLMResponseError(LLMError):
    """Raised when LLM returns an invalid response."""

    pass


class SearchError(NLFindError):
    """Base exception for search-related errors."""

    pass


class InvalidPathError(SearchError):
    """Raised when the search path is invalid."""

    pass


class PermissionDeniedError(SearchError):
    """Raised when access to a file or directory is denied."""

    pass


class ConfigError(NLFindError):
    """Base exception for configuration errors."""

    pass


class MissingAPIKeyError(ConfigError):
    """Raised when required API key is not configured."""

    pass


class InvalidConfigError(ConfigError):
    """Raised when configuration is invalid."""

    pass
