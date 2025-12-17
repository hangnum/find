# NL-Find: Natural Language File Search

**NL-Find** is an intelligent file search tool that allows you to find files on your system using natural language queries. It combines the power of Large Language Models (LLMs) with high-speed local search backends.

![GUI Screenshot](https://raw.githubusercontent.com/your-username/nl-find/main/docs/assets/gui-screenshot.png)
*(Note: Replace with an actual screenshot)*

## ✨ Features

- 🧠 **LLM-Powered Search**: Describe the files you want in plain language (e.g., "find large video files modified last week").
- ⚡ **High-Speed Backends**: Automatically uses the fastest available search tools on your system (`fd`, `Everything`, `find`).
- 💻 **Versatile Interfaces**: Use it as a fast command-line tool or a user-friendly GUI application.
- 🌐 **Provider Agnostic**: Compatible with any OpenAI API-compliant LLM provider (OpenAI, DeepSeek, Ollama, etc.).
- ⚙️ **Customizable**: Extensive configuration options for search behavior, LLM settings, and UI.
- fallback **Direct Search**: Bypass the LLM for traditional glob/pattern-based searches.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repo and install in editable mode
git clone https://github.com/your-username/nl-find.git
cd nl-find
pip install -e .

# Install GUI dependencies (PyQt6)
pip install -e ".[gui]"

# For best performance, install a native search backend (see "Search Backends" below)
# On Windows: winget install sharkdp.fd
# On macOS: brew install fd
```

### 2. Configuration

To use the natural language search, you need to configure an LLM API key.

Create a file named `.env` in the project root and add your details:

```env
# Example for OpenAI
OPENAI_API_KEY="sk-..."

# Example for a local Ollama server
LLM_BASE_URL="http://localhost:11434/v1"
LLM_API_KEY="ollama"
LLM_MODEL="llama3"
```

The tool will automatically load these settings. Alternatively, you can set them as environment variables.

### 3. Run a Search

```bash
# Use natural language to find recent large images
nfi search "find images larger than 5MB modified this week"

# Or use the GUI
python -m nl_find.gui.main_window
```

## 📖 Usage

### Command-Line Interface (CLI)

The `nfi search` command is the primary entry point.

```bash
# Natural language search (requires API key)
nfi search "show me python files I changed yesterday"

# Direct pattern search (no LLM needed)
nfi search "*.py" --no-llm --path ./src

# Search for files with specific content
nfi search "text files containing the word 'refactor'"

# Limit results and sort by size
nfi search "videos" --limit 10 --sort size --desc

# See all options
nfi search --help
```

### Graphical User Interface (GUI)

The GUI provides a familiar file-explorer-like experience.

```bash
python -m nl_find.gui.main_window
```

You can type a natural language query or a direct pattern into the search bar. Use the "LLM" checkbox to toggle between modes.

## ⚙️ Configuration

NL-Find is configured via environment variables or a `.env` file in the project root.

### LLM Settings (Prefix: `LLM_`)

- `LLM_API_KEY` or `OPENAI_API_KEY`: Your API key.
- `LLM_MODEL`: The model name (e.g., `gpt-4o-mini`, `llama3`).
- `LLM_BASE_URL`: The API endpoint URL for custom providers.
- `LLM_PROVIDER`: A descriptive name for your provider (e.g., `openai`, `ollama`).
- `LLM_TEMPERATURE`: Defaults to `0.0`.

### Search Settings (Prefix: `SEARCH_`)

- `SEARCH_BACKEND`: Set a preferred backend (`auto`, `fd`, `everything`, `find`, `python`). Defaults to `auto`.
- `SEARCH_DEFAULT_PATH`: The directory to search if `--path` is not specified.
- `SEARCH_MAX_RESULTS`: Default result limit. Defaults to `1000`.

## ⚡ Search Backends

NL-Find automatically selects the best available search tool for maximum speed.

| Backend      | Platform    | Speed     | Notes                                   |
|--------------|-------------|-----------|-----------------------------------------|
| `everything` | Windows     | ⚡⚡⚡⚡    | Instant results via NTFS indexing.      |
| `fd`         | Cross-Platform| ⚡⚡⚡     | A fast, modern `find` alternative. Recommended. |
| `find`       | Linux/macOS | ⚡⚡      | The standard, reliable Unix find tool.    |
| `python`     | Cross-Platform| ⚡         | The fallback backend, always available. |

### Installing Backends

```bash
# Windows: Install fd and/or Everything
winget install sharkdp.fd
# Or use the provided script to install Everything
# scripts\install_everything.bat

# macOS: Install fd via Homebrew
brew install fd

# Linux: Install fd via your package manager
sudo apt-get install fd-find  # Debian/Ubuntu
sudo dnf install fd-find      # Fedora
```

## 🛠️ Development

```bash
# Install all development dependencies
pip install -e ".[dev]"

# Format code
ruff format . && ruff check --fix . && black . && isort .

# Run tests
pytest -v
```

## 🏗️ Project Structure

```txt
.
├── .env.example      # Example environment file
├── pyproject.toml    # Project metadata and dependencies
├── README.md         # This file
├── requirements.txt
├── nl_find/
│   ├── cli/app.py        # CLI entry point (Typer)
│   ├── config/settings.py  # Configuration models (Pydantic)
│   ├── core/               # Core application logic
│   │   ├── backends.py     # Search backend implementations
│   │   ├── executor.py     # Main search execution orchestrator
│   │   ├── llm_parser.py   # Natural language parsing with LLM
│   │   └── models.py       # Data models (Pydantic)
│   ├── gui/main_window.py  # GUI entry point (PyQt6)
│   └── __main__.py       # Allows running with `python -m src`
├── tests/              # Unit and integration tests
└── docs/               # Project documentation
```

## 📄 License

This project is licensed under the MIT License.
