"""Unit tests for LLM parser module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from nl_find.core.exceptions import (
    LLMConnectionError,
    LLMParseError,
    LLMResponseError,
    MissingAPIKeyError,
)
from nl_find.core.llm_parser import LLMParser, _parse_size


class TestParseSize:
    """Tests for _parse_size function."""

    def test_parse_bytes(self):
        """Test parsing bytes."""
        assert _parse_size("100B") == 100
        assert _parse_size("1b") == 1

    def test_parse_kilobytes(self):
        """Test parsing kilobytes."""
        assert _parse_size("1KB") == 1024
        assert _parse_size("10kb") == 10 * 1024

    def test_parse_megabytes(self):
        """Test parsing megabytes."""
        assert _parse_size("1MB") == 1024**2
        assert _parse_size("10mb") == 10 * 1024**2

    def test_parse_gigabytes(self):
        """Test parsing gigabytes."""
        assert _parse_size("1GB") == 1024**3
        assert _parse_size("2gb") == 2 * 1024**3

    def test_parse_terabytes(self):
        """Test parsing terabytes."""
        assert _parse_size("1TB") == 1024**4

    def test_parse_decimal_values(self):
        """Test parsing decimal size values."""
        assert _parse_size("1.5MB") == int(1.5 * 1024**2)
        assert _parse_size("2.5GB") == int(2.5 * 1024**3)

    def test_parse_raw_integer_string(self):
        """Test parsing raw integer without unit."""
        assert _parse_size("1024") == 1024
        assert _parse_size("1048576") == 1048576

    def test_parse_with_whitespace(self):
        """Test parsing with surrounding whitespace."""
        assert _parse_size("  10MB  ") == 10 * 1024**2


class TestLLMParserInit:
    """Tests for LLMParser initialization."""

    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises MissingAPIKeyError."""
        with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
            mock_settings.return_value.llm.api_key = None
            with pytest.raises(MissingAPIKeyError):
                LLMParser()

    def test_init_with_explicit_api_key(self):
        """Test initialization with explicit API key."""
        with patch("nl_find.core.llm_parser.OpenAI"):
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = None
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser(api_key="test-key")
                assert parser.api_key == "test-key"

    def test_init_with_settings_api_key(self):
        """Test initialization with API key from settings."""
        with patch("nl_find.core.llm_parser.OpenAI"):
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "settings-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser()
                assert parser.api_key == "settings-key"


class TestGetDynamicPrompt:
    """Tests for _get_dynamic_prompt method."""

    def test_injects_current_date(self):
        """Test that dynamic prompt contains today's date."""
        with patch("nl_find.core.llm_parser.OpenAI"):
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser()
                prompt = parser._get_dynamic_prompt()

                today = datetime.now().date()
                yesterday = today - timedelta(days=1)
                week_ago = today - timedelta(days=7)

                assert today.isoformat() in prompt
                assert yesterday.isoformat() in prompt
                assert week_ago.isoformat() in prompt


class TestPreprocessLLMData:
    """Tests for _preprocess_llm_data method."""

    def test_converts_min_size_string(self):
        """Test converting min_size string to bytes."""
        with patch("nl_find.core.llm_parser.OpenAI"):
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser()
                data = {"min_size": "10MB", "extensions": [".py"]}
                result = parser._preprocess_llm_data(data)

                assert result["min_size"] == 10 * 1024**2
                assert result["extensions"] == [".py"]

    def test_converts_max_size_string(self):
        """Test converting max_size string to bytes."""
        with patch("nl_find.core.llm_parser.OpenAI"):
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser()
                data = {"max_size": "1GB"}
                result = parser._preprocess_llm_data(data)

                assert result["max_size"] == 1024**3

    def test_preserves_integer_sizes(self):
        """Test that integer sizes are not modified."""
        with patch("nl_find.core.llm_parser.OpenAI"):
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser()
                data = {"min_size": 1048576}
                result = parser._preprocess_llm_data(data)

                assert result["min_size"] == 1048576


class TestLLMParserParse:
    """Tests for parse method with mocked LLM responses."""

    def _create_mock_parser(self):
        """Create a parser with mocked dependencies."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                parser = LLMParser()
                return parser, mock_openai

    def test_parse_valid_json_response(self):
        """Test parsing valid JSON response."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai_class:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                # Mock the OpenAI client response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = '{"extensions": [".py"]}'

                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                parser = LLMParser()
                result = parser.parse("find Python files")

                assert result.extensions == [".py"]

    def test_parse_removes_markdown_code_blocks(self):
        """Test that markdown code blocks are stripped."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai_class:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = (
                    '```json\n{"extensions": [".txt"]}\n```'
                )

                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                parser = LLMParser()
                result = parser.parse("find text files")

                assert result.extensions == [".txt"]

    def test_parse_raises_on_empty_response(self):
        """Test that empty response raises LLMResponseError."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai_class:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = None

                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                parser = LLMParser()
                with pytest.raises(LLMResponseError):
                    parser.parse("test query")

    def test_parse_raises_on_invalid_json(self):
        """Test that invalid JSON raises LLMParseError."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai_class:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "not valid json"

                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                parser = LLMParser()
                with pytest.raises(LLMParseError):
                    parser.parse("test query")

    def test_parse_raises_on_connection_error(self):
        """Test that connection failure raises LLMConnectionError."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai_class:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                mock_client = MagicMock()
                mock_client.chat.completions.create.side_effect = Exception(
                    "Connection failed"
                )
                mock_openai_class.return_value = mock_client

                parser = LLMParser()
                with pytest.raises(LLMConnectionError):
                    parser.parse("test query")

    def test_parse_with_size_string_preprocessing(self):
        """Test that size strings in response are converted."""
        with patch("nl_find.core.llm_parser.OpenAI") as mock_openai_class:
            with patch("nl_find.core.llm_parser.get_settings") as mock_settings:
                mock_settings.return_value.llm.api_key = "test-key"
                mock_settings.return_value.llm.model = "gpt-4"
                mock_settings.return_value.llm.temperature = 0.0
                mock_settings.return_value.llm.max_tokens = 1024
                mock_settings.return_value.llm.base_url = None

                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = (
                    '{"min_size": "10MB", "extensions": [".py"]}'
                )

                mock_client = MagicMock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                parser = LLMParser()
                result = parser.parse("find large Python files")

                assert result.min_size == 10 * 1024**2
