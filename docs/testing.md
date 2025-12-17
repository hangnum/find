# NL-Find Testing Guidelines

This document outlines the standards and best practices for writing tests in the NL-Find project.

## 1. Testing Frameworks

- **`pytest`**: The primary framework for writing and running tests.
- **`pytest-cov`**: For measuring test coverage.
- **`pytest-mock`**: For creating mocks and patching objects.
- **`pytest-asyncio`**: For testing asynchronous code (if any).

---

## 2. Directory Structure

All tests are located in the `tests/` directory.

```txt
tests/
├── conftest.py          # Shared fixtures (e.g., for creating temp files)
├── test_backends.py     # Tests for all search backends
├── test_executor.py     # Tests for the SearchExecutor
├── test_models.py       # Tests for the Pydantic data models
├── test_parser.py       # Tests for the LLMParser (planned)
├── test_settings.py     # Tests for the configuration system
└── test_cli.py          # End-to-end tests for the CLI (planned)
```

---

## 3. Test Naming Conventions

- **Test Files**: Must start with `test_` (e.g., `test_executor.py`).
- **Test Functions**: Must start with `test_` and describe the behavior being tested (e.g., `test_executor_returns_correct_file_count`).
- **Fixtures**: Use clear, descriptive lowercase names (e.g., `sample_directory`, `mock_openai_client`).

---

## 4. Writing Good Tests

### The AAA Pattern (Arrange, Act, Assert)

Structure your tests clearly using the AAA pattern.

```python
def test_search_for_python_files():
    # 1. Arrange - Set up the test conditions
    # (e.g., create temporary files, initialize the executor)
    with create_test_directory({"file.py": "", "file.txt": ""}) as temp_dir:
        query = SearchQuery(path=temp_dir, extensions=[".py"])
        params = SearchParams(query=query)
        executor = SearchExecutor()

        # 2. Act - Call the code being tested
        result = executor.execute(params)

        # 3. Assert - Check if the outcome is as expected
        assert result.total_count == 1
        assert result.files[0].name == "file.py"
```

### Use Fixtures for Setup and Teardown

Use `pytest` fixtures to manage shared resources and setup/teardown logic. Place reusable fixtures in `tests/conftest.py`.

```python
# In conftest.py
@pytest.fixture
def temp_directory_with_files(tmp_path):
    """Creates a temporary directory with a few files for testing."""
    (tmp_path / "test.py").touch()
    (tmp_path / "image.jpg").touch()
    (tmp_path / "docs/readme.md").mkdir(parents=True)
    return tmp_path

# In a test file
def test_search_in_directory(temp_directory_with_files):
    # The fixture provides the populated directory
    params = SearchParams(query=SearchQuery(path=temp_directory_with_files))
    executor = SearchExecutor()
    result = executor.execute(params)
    assert result.total_count == 3
```

### Mock External Services

Mock external services like the LLM API to make tests fast, deterministic, and independent of network or API keys.

```python
def test_parser_uses_mocked_llm_response(mocker):
    # Arrange: Mock the OpenAI client's completion create method
    mock_response = {"choices": [{"message": {"content": '{"pattern": "*.py"}'}}]}
    mocker.patch(
        "openai.resources.chat.completions.Completions.create",
        return_value=mock_response
    )
    
    # Act
    parser = LLMParser(api_key="fake-key")
    search_query = parser.parse("any python files")

    # Assert
    assert search_query.pattern == "*.py"
```

---

## 5. Running Tests

### Commands

```bash
# Run all tests
pytest -v

# Run tests and generate an HTML coverage report
pytest --cov=src --cov-report=html

# Run only tests in a specific file
pytest tests/test_executor.py

# Run tests with a specific marker
pytest -m "slow"
```

### Test Markers

Use markers to categorize tests.

- `@pytest.mark.slow`: For tests that take a significant amount of time.
- `@pytest.mark.requires_api`: For tests that make real API calls (should be used sparingly and skipped in CI).
- `@pytest.mark.parametrize`: To run the same test with different inputs.

```python
@pytest.mark.parametrize(
    "query, expected_pattern",
    [
        ("python files", "*.py"),
        ("text files", "*.txt"),
    ]
)
def test_file_type_parsing(query, expected_pattern):
    # ... test logic ...
```

## 6. Coverage Requirements

Strive for high test coverage, especially for the core logic.

| Module          | Minimum Coverage |
|-----------------|------------------|
| `src/core/`     | 85%              |
| `src/config/`   | 90%              |
| `src/cli/`      | 70%              |

Check coverage by opening `htmlcov/index.html` after running `pytest --cov`.
