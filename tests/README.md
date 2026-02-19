# Tests for changes-roller

This directory contains comprehensive tests for the changes-roller project.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py             # Shared pytest fixtures
├── test_cli.py             # CLI interface tests
├── test_config.py          # Configuration parsing tests
├── test_executor.py        # Patch executor tests
├── test_integration.py     # Integration tests
├── test_reporter.py        # Output reporter tests
├── test_repository.py      # Git repository operations tests
└── test_workspace.py       # Workspace management tests
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_config.py
```

### Run specific test

```bash
pytest tests/test_config.py::TestConfigParser::test_parse_valid_config
```

### Run with coverage report

```bash
pytest --cov=roller --cov-report=html
```

### Run only unit tests

```bash
pytest -m unit
```

### Run only integration tests

```bash
pytest -m integration
```

## Test Coverage

To view current test coverage:

```bash
# Generate coverage report
pytest --cov=roller --cov-report=term-missing

# Generate HTML report
pytest --cov=roller --cov-report=html
# Open htmlcov/index.html in your browser
```

The project maintains comprehensive test coverage across all modules. Some modules have lower coverage due to complex integration scenarios that require actual file system operations and parallel processing.

## Test Categories

### Unit Tests

- **test_config.py**: Tests configuration file parsing, validation, and error handling
- **test_workspace.py**: Tests workspace creation, cleanup, and path management
- **test_reporter.py**: Tests output formatting and result tracking
- **test_repository.py**: Tests Git operations with mocked subprocess calls
- **test_executor.py**: Tests patch execution logic with mocked repositories
- **test_cli.py**: Tests CLI commands with mocked dependencies

### Integration Tests

- **test_integration.py**: End-to-end workflow tests with full component integration

## Key Fixtures

Defined in `conftest.py`:

- `temp_dir`: Temporary directory for test files
- `sample_config_content`: Sample configuration file content
- `minimal_config_content`: Minimal valid configuration
- `config_file`: Temporary configuration file
- `sample_series_config`: Pre-configured SeriesConfig object
- `executable_script`: Test script for patch execution

## Writing New Tests

### Test Naming Convention

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_is_being_tested>`

### Example Test

```python
def test_parse_valid_config(config_file: Path):
    """Test parsing a valid configuration file."""
    parser = ConfigParser(config_file)
    config = parser.parse()

    assert config.projects == ["https://github.com/org/repo1.git"]
    assert config.commands == "./patch.sh"
```

### Using Mocks

```python
@patch('roller.executor.Repository')
def test_process_repository(mock_repo_class):
    """Test repository processing."""
    mock_repo = MagicMock()
    mock_repo.clone.return_value = True
    mock_repo_class.return_value = mock_repo

    # Test code here
```

## Continuous Integration

Tests are configured to run automatically on:

- Every push to the repository
- Every pull request
- Coverage reports are generated and tracked

## Requirements

Test dependencies are defined in `pyproject.toml`:

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
]
```

Install test dependencies:

```bash
pip install -e ".[test]"
```
