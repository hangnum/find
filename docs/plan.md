# NL-Find Project Plan

This document outlines the development plan, phases, and milestones for the NL-Find project.

## 1. Project Overview

**NL-Find** is a file search utility that uses Large Language Models (LLMs) to enable searching with natural language queries. It provides both a Command-Line Interface (CLI) for power users and a Graphical User Interface (GUI) for visual interaction.

---

## 2. Technology Stack

| Component         | Technology / Library                                       |
|-------------------|------------------------------------------------------------|
| **Language**      | Python 3.11+                                               |
| **CLI**           | Typer, Rich                                                |
| **GUI**           | PyQt6                                                      |
| **LLM Integration** | `openai` library (compatible with any OpenAI-like API)     |
| **Configuration** | Pydantic Settings                                          |
| **Testing**       | Pytest                                                     |
| **Formatting**    | Black, isort, Ruff                                         |

---

## 3. Development Phases

### Phase 1: Core Engine ✅

- [x] **Project Scaffolding**: Set up the initial directory structure, `pyproject.toml`, and Git repository.
- [x] **Data Models**: Define core data structures (`SearchQuery`, `FileInfo`, etc.) using Pydantic.
- [x] **LLM Parser**: Implement the `LLMParser` to convert natural language into a `SearchQuery`.
- [x] **Search Executor**: Implement the `SearchExecutor` to orchestrate searches.
- [x] **Pluggable Backends**: Create the backend system and implement the `PythonBackend` as a fallback.
- [x] **Unit Tests**: Write initial tests for the core components.

### Phase 2: Advanced Backends & CLI ✅

- [x] **High-Speed Backends**: Implement `FdBackend`, `EverythingBackend`, and `FindBackend`.
- [x] **Backend Selection**: Implement auto-selection logic for the best available backend.
- [x] **CLI Implementation**: Build the Typer-based CLI with the `search` command and options.
- [x] **CLI Output**: Format and display results in the console using Rich.

### Phase 3: GUI Implementation ✅

- [x] **Main Window Layout**: Design and implement the main window with a file manager style.
- [x] **Core Widgets**: Build the `DirectoryTree`, `FileListWidget`, and `SearchBar` components.
- [x] **Background Searches**: Implement `QThread` worker to run searches without freezing the UI.
- [x] **Signal/Slot Connections**: Wire up the GUI components to interact with the core engine.
- [ ] **File Preview Panel**: (Optional) Add a panel to show a preview of the selected file.
- [ ] **Theme Switching**: (Optional) Allow users to switch between light and dark themes.

### Phase 4: Refinement & Packaging 🚧

- [x] **Configuration System**: Implement a robust configuration system using Pydantic Settings (`.env` support).
- [ ] **Integration Testing**: Add end-to-end tests for CLI and GUI workflows.
- [🚧] **User Documentation**: Write comprehensive user and developer documentation.
- [ ] **Packaging**: Create distributable packages using PyInstaller or a similar tool.
- [ ] **CI/CD**: Set up a GitHub Actions workflow for automated testing and linting.

---

## 4. Milestones

| Milestone | Goal                                         | Status      |
|-----------|----------------------------------------------|-------------|
| **M1**    | Core engine and basic CLI are functional.    | ✅ Complete |
| **M2**    | Advanced backends and a feature-complete CLI.| ✅ Complete |
| **M3**    | A functional GUI is available.               | ✅ Complete |
| **M4**    | Project is well-documented and packageable.  | 🚧 In Progress |
| **v1.0**  | First official release.                      | ⏳ Pending   |
