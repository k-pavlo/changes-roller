# Contributing to changes-roller

Thank you for your interest in contributing! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)
- [For Maintainers](#for-maintainers)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/changes-roller.git
cd changes-roller

# 2. Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev,test,docs]"

# 3. Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# 4. Create a branch and make changes
git checkout -b feature/my-feature

# 5. Run tests
pytest

# 6. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: description of changes"

# 7. Push and create PR
git push origin feature/my-feature
```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git command-line client
- pip package manager

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/changes-roller.git
cd changes-roller

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

### Verify Installation

```bash
# Run the CLI
roller --help

# Run tests
pytest

# Verify pre-commit hooks
pre-commit run --all-files
```

## Code Quality

This project uses automated tools to maintain code quality.

### Tools

- **Ruff** - Linting and formatting
- **MyPy** - Strict type checking
- **Bandit** - Security scanning
- **Pytest** - Testing

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit to:

- Format code (Ruff)
- Lint code (Ruff)
- Type check (MyPy)
- Security scan (Bandit)
- Validate files (YAML, TOML, whitespace, etc.)
- Enforce conventional commit messages

**Usage:**

```bash
# Hooks run automatically on commit
git commit -m "feat: add new feature"

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff

# Skip hooks (not recommended)
git commit --no-verify
```

**If hooks modify files:**

1. Pre-commit auto-fixes issues (formatting, whitespace)
2. Review the changes: `git diff`
3. Stage the fixes: `git add .`
4. Commit again: `git commit -m "feat: add new feature"`

### Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/).

**Format:**

```
<type>(<optional scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat:` - New feature (MINOR version bump)
- `fix:` - Bug fix (PATCH version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements
- `ci:` - CI/CD changes

**Examples:**

```bash
git commit -m "feat: add support for custom git branches"
git commit -m "fix: handle edge case in path resolution"
git commit -m "docs: update installation instructions"
```

**Breaking changes:**

```bash
git commit -m "feat!: redesign CLI interface

BREAKING CHANGE: The --output flag has been renamed to --destination"
```

### Code Style Guidelines

- Follow PEP 8 (enforced by Ruff)
- Maximum line length: 88 characters
- Use type hints for all function signatures
- Write docstrings for public modules, classes, and functions
- Keep functions focused and small

### Manual Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check .
ruff check --fix .  # Auto-fix issues

# Type check
mypy roller/

# Security scan
bandit -c pyproject.toml -r roller/

# Run all checks
pre-commit run --all-files
```

## Testing

All code changes must include appropriate tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=roller --cov-report=term-missing

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_cli.py::test_init_command
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures from `conftest.py`
- Mock external dependencies (git commands, file operations)
- Aim for high code coverage

### Test Organization

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test multiple components working together
- Use markers: `@pytest.mark.unit` or `@pytest.mark.integration`

### Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Tests must pass before submitting a PR
- Maintain or improve code coverage

## Documentation

We use Sphinx to generate documentation hosted on [ReadTheDocs](https://changes-roller.readthedocs.io).

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build HTML documentation
cd docs
sphinx-build -b html . _build/html

# View documentation
# Open docs/_build/html/index.html in your browser

# Serve with live reload (optional)
python -m http.server --directory _build/html 8000
# Then open http://localhost:8000

# Clean build artifacts
make clean  # or rm -rf _build
```

### Documentation Guidelines

- Use Markdown (`.md`) for most pages
- Follow existing structure and style
- Include code examples where appropriate
- Update docs when adding features or changing behavior
- Preview docs locally before submitting

### ReadTheDocs Integration

- Documentation builds automatically on every commit to main
- PR previews are available for documentation changes
- View live docs at: https://changes-roller.readthedocs.io

## Submitting Changes

### Before Submitting

1. **Ensure tests pass**: `pytest`
2. **Run quality checks**: `pre-commit run --all-files`
3. **Update documentation** if needed
4. **Use conventional commit messages**

### Pull Request Process

1. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards

3. **Commit with conventional commits**:

   ```bash
   git add .
   git commit -m "feat: description of changes"
   # Pre-commit hooks run automatically
   ```

4. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** on GitHub:
   - Provide a clear title and description
   - Reference any related issues
   - Explain what changed and why
   - Include testing instructions if applicable

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Write clear commit messages
- Update tests and documentation
- Respond to review feedback promptly
- Ensure CI checks pass

### Continuous Integration

All PRs automatically run:

**Code Quality** (~2 min):

- Ruff formatting and linting
- File validation (YAML, TOML, whitespace)
- Prettier (Markdown, JSON)

**Type Checking** (~2 min):

- MyPy strict type checking

**Tests** (~5-10 min):

- Tests on Python 3.10, 3.11, 3.12, 3.13
- Tests on Linux, macOS, Windows
- Coverage reporting (Codecov)

**Security** (~2 min):

- Bandit code security scan
- pip-audit dependency vulnerabilities
- Dependency Review for PRs

All checks must pass before merging.

**If CI fails:**

- Click "Details" next to the failed check to view logs
- Fix issues locally: `pre-commit run --all-files` and `pytest`
- Push fixes to your branch (CI will re-run automatically)

## Issue Reporting

### Creating Issues

Use the appropriate issue template:

- **Bug Report** - Report bugs or unexpected behavior
- **Feature Request** - Suggest new features or enhancements
- **Documentation** - Suggest documentation improvements

### Before Creating an Issue

- Search existing issues to avoid duplicates
- Check if issue is fixed in the latest version
- Gather relevant information (version, platform, error messages)

### Bug Reports Should Include

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, changes-roller version)
- Error messages and stack traces
- Configuration files (if relevant)

### Feature Requests Should Include

- Clear description of desired functionality
- Use cases and motivation
- Proposed implementation approach
- Impact on your workflow
- Willingness to contribute

### Questions and Discussions

For usage questions:

- Check [README](README.md) and [documentation](https://changes-roller.readthedocs.io) first
- Search closed issues for similar questions
- Open a [GitHub Discussion](https://github.com/k-pavlo/changes-roller/discussions)
- For security issues, see [SECURITY.md](SECURITY.md)

## For Maintainers

This project has automated versioning and releases.

**For maintainers, see:**

- **[RELEASING.md](RELEASING.md)** - Version bumping and release process
- **[.github/workflows/README.md](.github/workflows/README.md)** - CI/CD pipeline details

**Quick summary:**

1. PRs are merged to main with conventional commit messages
2. When ready to release, run `cz bump` to calculate version and update files
3. Push the version tag: `git push --tags`
4. GitHub Actions automatically builds and publishes to PyPI
5. GitHub Release is created automatically with release notes

For detailed instructions, see [RELEASING.md](RELEASING.md).

---

Thank you for contributing to changes-roller!
