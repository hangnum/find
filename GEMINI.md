# Gemini Agent Project Brief: NL-Find

This document provides a high-level overview of the **NL-Find** project, its architecture, and development conventions. It is intended to be a starting point for an AI agent developer.

## 1. Project Objective

NL-Find is a functional Python application that enables users to search for files using natural language. It integrates with Large Language Models (LLMs) to parse queries and uses optimized backend tools to perform fast and accurate file system searches. The project has both a command-line (CLI) and a graphical (GUI) interface.

## 2. Current Status

The project has implementations for its core engine, CLI, and GUI. It is a functional application that can be run and tested. Key features like natural language parsing, pluggable search backends, and user configuration are in place.

## 3. Key Components & Architecture

The application is built on a three-layer architecture: **UI**, **Core Engine**, and **Infrastructure**.

- **`src/cli/app.py` (Typer)**: The command-line interface.
- **`src/gui/main_window.py` (PyQt6)**: The graphical user interface.
- **`src/core/llm_parser.py`**: The `LLMParser` class uses an LLM to convert natural language queries into a structured `SearchQuery` Pydantic model.
- **`src/core/executor.py`**: The `SearchExecutor` takes a `SearchQuery` and orchestrates the search.
- **`src/core/backends.py`**: Defines the pluggable search backends (`fd`, `Everything`, `find`, `python`), which are selected based on availability and user preference.
- **`src/core/models.py`**: Contains all Pydantic data models for structured data transfer (e.g., `SearchQuery`, `FileInfo`).
- **`src/config/settings.py`**: Manages application configuration using `pydantic-settings`, loading from environment variables and `.env` files.

## 4. Building and Running

### Installation

```bash
# Install base dependencies in editable mode
pip install -e .

# Install GUI dependencies
pip install -e ".[gui]"

# Install development dependencies
pip install -e ".[dev]"
```

### Running the Application

```bash
# Run the CLI (requires configuration, see README.md)
nfi search "find recent python files"

# Run the GUI
python -m src.gui.main_window
```

## 5. Development Conventions

Strict adherence to the project's established conventions is required. Refer to the `docs` directory for detailed guidelines.

### Code Style (`docs/code_style.md`)

- **Formatting**: `black`, `isort`, `ruff`. All tools are configured in `pyproject.toml`.
- **Type Hinting**: All public functions must be fully type-annotated.
- **Docstrings**: Google-style docstrings are required for all public modules and functions.
- **Logging**: Use the `loguru` library for logging.

### Git Conventions (`docs/git_conventions.md`)

- **Commits**: Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification (e.g., `feat:`, `fix:`, `docs:`).

### Testing (`docs/testing.md`)

- **Framework**: `pytest` is used for all tests.
- **Execution**: All new code (features or fixes) should be accompanied by corresponding tests.

### Commands

- **Formatting & Linting**:

  ```bash
  ruff format . && ruff check --fix . && black . && isort .
  ```

- **Testing**:

  ```bash
  pytest -v
  ```

## 6. Agent Directives

As an agent, you need to act as a senior software engineer who highly adheres to software engineering standards.

- **Deep Analysis**: Rely on long-term thinking, serialize your thinking process, and analyze problems deeply.
- **Verification**: Every step needs to be fully thought out and verified.
- **Planning**: Through detailed planning, design executable plans in advance to effectively avoid errors.
- **Architecture**: The architecture design should fully consider scalability, maintainability, and testability.
- **Code Quality**: The code should maintain a low degree of coupling.
