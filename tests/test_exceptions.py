"""Unit tests for exceptions module."""

import pytest

from src.core.exceptions import (
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


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_base_exception(self):
        """Test NLFindError is the base for all exceptions."""
        assert issubclass(LLMError, NLFindError)
        assert issubclass(SearchError, NLFindError)
        assert issubclass(ConfigError, NLFindError)

    def test_llm_exceptions_inherit_llm_error(self):
        """Test LLM exceptions inherit from LLMError."""
        assert issubclass(LLMConnectionError, LLMError)
        assert issubclass(LLMParseError, LLMError)
        assert issubclass(LLMResponseError, LLMError)

    def test_search_exceptions_inherit_search_error(self):
        """Test search exceptions inherit from SearchError."""
        assert issubclass(InvalidPathError, SearchError)
        assert issubclass(PermissionDeniedError, SearchError)

    def test_config_exceptions_inherit_config_error(self):
        """Test config exceptions inherit from ConfigError."""
        assert issubclass(MissingAPIKeyError, ConfigError)
        assert issubclass(InvalidConfigError, ConfigError)


class TestExceptionMessages:
    """Tests for exception message handling."""

    def test_exception_with_message(self):
        """Test exceptions can be created with messages."""
        msg = "Test error message"
        exc = NLFindError(msg)
        assert str(exc) == msg

    def test_llm_connection_error_message(self):
        """Test LLMConnectionError with detailed message."""
        exc = LLMConnectionError("Connection timeout after 30s")
        assert "timeout" in str(exc).lower()

    def test_invalid_path_error_message(self):
        """Test InvalidPathError with path info."""
        exc = InvalidPathError("Path does not exist: /nonexistent")
        assert "/nonexistent" in str(exc)

    def test_missing_api_key_error(self):
        """Test MissingAPIKeyError message."""
        exc = MissingAPIKeyError("OPENAI_API_KEY not set")
        assert "OPENAI_API_KEY" in str(exc)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_catch_by_base_class(self):
        """Test catching specific exception by base class."""
        with pytest.raises(NLFindError):
            raise LLMConnectionError("test")

    def test_catch_by_intermediate_class(self):
        """Test catching by intermediate class."""
        with pytest.raises(LLMError):
            raise LLMParseError("invalid json")

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(InvalidPathError):
            raise InvalidPathError("not found")

    def test_exception_chaining(self):
        """Test exception chaining with cause."""
        original = ValueError("original error")
        try:
            raise LLMParseError("parse failed") from original
        except LLMParseError as e:
            assert e.__cause__ is original
