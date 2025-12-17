"""Unit tests for configuration settings."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config.settings import (
    LLMSettings,
    SearchSettings,
    Settings,
    UISettings,
    get_settings,
    reset_settings,
)


class TestLLMSettings:
    """Tests for LLM configuration."""

    def test_default_values(self):
        """Test default LLM settings."""
        settings = LLMSettings()
        assert settings.provider == "openai"
        assert settings.model == "gpt-4o-mini"
        assert settings.temperature == 0.0
        assert settings.max_tokens == 1024

    def test_api_key_from_env(self):
        """Test API key loading from environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
            settings = LLMSettings()
            assert settings.api_key == "test-key-123"

    def test_custom_model(self):
        """Test setting custom model."""
        settings = LLMSettings(model="gpt-4o")
        assert settings.model == "gpt-4o"

    def test_ollama_provider(self):
        """Test Ollama provider configuration."""
        settings = LLMSettings(provider="ollama", base_url="http://localhost:11434")
        assert settings.provider == "ollama"
        assert settings.base_url == "http://localhost:11434"

    def test_custom_provider(self):
        """Test custom provider name (e.g., DeepSeek)."""
        settings = LLMSettings(
            provider="deepseek",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
        )
        assert settings.provider == "deepseek"
        assert settings.base_url == "https://api.deepseek.com/v1"
        assert settings.model == "deepseek-chat"

    def test_api_key_from_llm_prefix(self):
        """Test API key loading from LLM_API_KEY environment variable."""
        with patch.dict(os.environ, {"LLM_API_KEY": "llm-key-456"}, clear=False):
            settings = LLMSettings()
            assert settings.api_key == "llm-key-456"

    def test_api_key_priority(self):
        """Test LLM_API_KEY takes priority over OPENAI_API_KEY."""
        with patch.dict(
            os.environ,
            {"LLM_API_KEY": "llm-key", "OPENAI_API_KEY": "openai-key"},
            clear=False,
        ):
            settings = LLMSettings()
            # LLM_API_KEY should be checked first
            assert settings.api_key == "llm-key"


class TestSearchSettings:
    """Tests for search configuration."""

    def test_default_values(self):
        """Test default search settings."""
        settings = SearchSettings()
        assert settings.max_results == 1000
        assert settings.include_hidden is False
        assert settings.recursive is True

    def test_custom_max_results(self):
        """Test custom max results."""
        settings = SearchSettings(max_results=500)
        assert settings.max_results == 500

    def test_include_hidden_files(self):
        """Test include hidden files option."""
        settings = SearchSettings(include_hidden=True)
        assert settings.include_hidden is True

    def test_non_recursive_search(self):
        """Test non-recursive search option."""
        settings = SearchSettings(recursive=False)
        assert settings.recursive is False


class TestUISettings:
    """Tests for UI configuration."""

    def test_default_values(self):
        """Test default UI settings."""
        settings = UISettings()
        assert settings.theme == "dark"
        assert settings.language == "zh_CN"
        assert settings.show_preview is True

    def test_light_theme(self):
        """Test light theme setting."""
        settings = UISettings(theme="light")
        assert settings.theme == "light"

    def test_english_language(self):
        """Test English language setting."""
        settings = UISettings(language="en_US")
        assert settings.language == "en_US"


class TestSettings:
    """Tests for main Settings class."""

    def test_default_settings(self):
        """Test default settings initialization."""
        settings = Settings()
        assert isinstance(settings.llm, LLMSettings)
        assert isinstance(settings.search, SearchSettings)
        assert isinstance(settings.ui, UISettings)

    def test_nested_settings(self):
        """Test nested settings access."""
        settings = Settings()
        assert settings.llm.provider == "openai"
        assert settings.search.max_results == 1000
        assert settings.ui.theme == "dark"


class TestGetSettings:
    """Tests for get_settings() singleton pattern."""

    def setup_method(self):
        """Reset settings before each test."""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test."""
        reset_settings()

    def test_get_settings_returns_settings(self):
        """Test get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_singleton(self):
        """Test get_settings returns same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_reset_settings(self):
        """Test reset_settings creates new instance."""
        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()
        assert settings1 is not settings2
