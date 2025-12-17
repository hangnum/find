# NL-Find: Natural Language File Search

## Project Overview

NL-Find is a Python-based utility designed to search for files using natural language queries. It leverages a Large Language Model (LLM) to parse user input and translate it into file system search commands. The project is planned to have both a Command-Line Interface (CLI) built with Typer and a Graphical User Interface (GUI) built with PyQt6.

The architecture is composed of three main layers:

1. **User Interface Layer:** CLI and GUI for user interaction.
2. **Core Engine Layer:** Handles the core logic of parsing queries, generating search commands, and executing the search.
3. **Infrastructure Layer:** Manages interactions with the LLM, file system, and configuration.

The project is in its early planning and setup stages. The core source code is not yet implemented, but the project structure and development guidelines are well-documented.

## Building and Running

The project is not yet runnable. However, the development conventions specify the tools and commands for linting, formatting, and testing.

### Linting and Formatting

The project uses `black` for formatting, `isort` for import sorting, and `ruff` for linting.

```bash
# Format, sort imports, and lint the code
black . && isort . && ruff check --fix .
```

### Testing

The project uses `pytest` for testing.

```bash
# Run tests
pytest
```

## Development Conventions

### Code Style

- **Formatting:** `black` (line width 88), `isort`, `ruff`.
- **Type Hinting:** All public functions must be type-annotated.
- **Naming:** `snake_case` for modules and functions/variables, `PascalCase` for classes.
- **Docstrings:** Google-style docstrings are required.
- **Error Handling:** Custom exceptions are defined in `src/core/exceptions.py`. Avoid bare `except:` clauses.
- **Logging:** Use `loguru` or the standard `logging` library.
- **Configuration:** `pydantic-settings` is used for configuration management. API keys and other secrets are loaded from environment variables, while user settings are stored in `config.yaml`.

### Git and Versioning

- **Branching:** A `main`/`dev` branching model is used, with feature, fix, and refactor branches.
- **Commits:** The project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.
- **Pull Requests:** PRs should have a descriptive title and follow the provided template.
- **Versioning:** [Semantic Versioning (SemVer)](https://semver.org/) is used for versioning.

### 运行环境

conda base 环境下运行

### 要求

代码风格遵循docs/code_style.md
项目架构遵循docs/architecture.md
项目计划遵循docs/plan.md
项目提交规范遵循docs/git_conventions.md
测试规范遵循docs/testing.md

严禁乱提交，必须按照文档中的规范进行提交
禁止随意放文档，文档和测试文件必须放置在固定的文件夹下
完成子任务之后，及时进行测试，更新文档，以及提交
