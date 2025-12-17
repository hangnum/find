"""Configuration settings for NL-Find."""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM provider settings.

    Attributes:
        provider: LLM provider name (openai or ollama).
        model: Model name to use.
        api_key: API key for the provider.
        base_url: Base URL for the API endpoint.
        temperature: Temperature for response generation.
        max_tokens: Maximum tokens in response.
    """

    model_config = SettingsConfigDict(env_prefix="LLM_")

    provider: Literal["openai", "ollama"] = "openai"
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 1024


class SearchSettings(BaseSettings):
    """Search behavior settings.

    Attributes:
        default_path: Default search path.
        max_results: Maximum number of results to return.
        include_hidden: Whether to include hidden files by default.
        recursive: Whether to search recursively by default.
    """

    model_config = SettingsConfigDict(env_prefix="SEARCH_")

    default_path: Path = Field(default_factory=Path.cwd)
    max_results: int = 1000
    include_hidden: bool = False
    recursive: bool = True


class UISettings(BaseSettings):
    """UI settings.

    Attributes:
        theme: UI theme (dark or light).
        language: UI language.
        show_preview: Whether to show file preview panel.
    """

    model_config = SettingsConfigDict(env_prefix="UI_")

    theme: Literal["dark", "light"] = "dark"
    language: str = "zh_CN"
    show_preview: bool = True


class Settings(BaseSettings):
    """Main application settings.

    Attributes:
        llm: LLM configuration.
        search: Search behavior configuration.
        ui: UI configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm: LLMSettings = Field(default_factory=LLMSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    ui: UISettings = Field(default_factory=UISettings)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance.

    Returns:
        The global Settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset global settings (useful for testing)."""
    global _settings
    _settings = None
