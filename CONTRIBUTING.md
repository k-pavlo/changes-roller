# Contributing to changes-roller

Thank you for your interest in contributing to changes-roller! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Versioning](#versioning)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a new branch for your changes
5. Make your changes
6. Run tests and quality checks
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git command-line client
- pip package manager

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/changes-roller.git
cd changes-roller

# Create a virtual environment
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
# Run the CLI to verify installation
roller --help

# Run tests to ensure everything works
pytest

# Verify pre-commit hooks are working
pre-commit run --all-files
```

## Code Standards

This project maintains high code quality standards using automated tools.

### Code Formatting and Linting

We use **Ruff** for both linting and formatting:

```bash
# Format code
ruff format .

# Run linter
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### Type Checking

We use **MyPy** with strict type checking enabled:

```bash
# Run type checker
mypy roller/
```

All code must include type hints. Configuration is in `pyproject.toml` under `[tool.mypy]`.

### Code Style Guidelines

- Follow PEP 8 conventions (enforced by Ruff)
- Maximum line length: 88 characters
- Use double quotes for strings
- Use type hints for all function signatures
- Write descriptive variable and function names
- Add docstrings for public modules, classes, and functions

### Pre-commit Hooks

This project uses **pre-commit hooks** to automatically enforce code quality standards before commits.

#### What Pre-commit Does

Pre-commit hooks automatically run before every commit to:

- **Format code** with Ruff formatter
- **Lint code** with Ruff linter (catches bugs and style issues)
- **Type check** with MyPy (ensures type safety)
- **Security scan** with Bandit (detects security vulnerabilities)
- **Validate files** (YAML, TOML syntax)
- **Fix common issues** (trailing whitespace, end of file)
- **Enforce commit message format** (conventional commits)

#### Installation

Pre-commit hooks are installed during initial setup:

```bash
pre-commit install                    # Install pre-commit hook
pre-commit install --hook-type commit-msg  # Install commit-msg hook
```

#### Usage

Once installed, hooks run automatically on `git commit`. You can also run them manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run a specific hook
pre-commit run ruff

# Skip hooks (not recommended, use only when necessary)
git commit --no-verify
```

#### Commit Message Format

This project follows [Conventional Commits](https://www.conventionalcommits.org/). Commit messages must follow this format:

```
<type>(<optional scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks (dependencies, config)
- `perf:` Performance improvements
- `ci:` CI/CD changes

**Examples:**

```bash
git commit -m "feat: add support for custom git branches"
git commit -m "fix: handle edge case in path resolution"
git commit -m "docs: update installation instructions"
git commit -m "chore: update dependencies"
```

#### Troubleshooting

If pre-commit fails:

1. **Read the error message** - it tells you what's wrong
2. **Auto-fixes** - Some hooks automatically fix issues (run `git add` again)
3. **Manual fixes** - Fix issues identified by linter or type checker
4. **Re-run** - After fixing, commit again (hooks will re-run)

Example workflow when hooks fail:

```bash
$ git commit -m "feat: add new feature"
# Hooks run and some fail...
# Some files are auto-fixed (formatter, trailing whitespace)

$ git add .  # Stage the auto-fixed files
$ git commit -m "feat: add new feature"  # Commit again
# All hooks pass!
```

## Testing

All code changes must include appropriate tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=roller --cov-report=term-missing

# Run specific test file
pytest tests/test_cli.py

# Run tests matching a pattern
pytest -k "test_apply"
```

### Test Organization

- Unit tests: Test individual functions and classes in isolation
- Integration tests: Test multiple components working together
- Use markers: `@pytest.mark.unit` or `@pytest.mark.integration`

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for common setup
- Mock external dependencies (git commands, file operations)
- Aim for >90% code coverage

### Test Requirements

- All new features must include tests
- Bug fixes should include regression tests
- Tests must pass before submitting a PR
- Maintain or improve code coverage

## Submitting Changes

### Before Submitting

1. **Quality checks run automatically:**

   Pre-commit hooks automatically run before each commit to check:
   - Code formatting (Ruff)
   - Linting (Ruff)
   - Type checking (MyPy)
   - Security scanning (Bandit)
   - File validation (YAML, TOML)

   You can also run checks manually:

   ```bash
   # Run all pre-commit hooks
   pre-commit run --all-files

   # Or run individual tools
   ruff format .
   ruff check .
   mypy roller/
   pytest
   ```

2. **Ensure all tests pass**
3. **Update documentation if needed**
4. **Add entries to CHANGELOG.md** (see Versioning section)
5. **Use conventional commit messages** (enforced by commitizen hook)

### Pull Request Process

1. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards

3. **Commit your changes** with clear, descriptive messages:

   ```bash
   git add .
   git commit -m "Add feature: description of what changed"
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

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backwards compatible)
- **PATCH** version for backwards compatible bug fixes

### Changelog

We maintain a changelog following [Keep a Changelog v1.0.0](https://keepachangelog.com/en/1.0.0/) format.

When submitting a PR, add an entry to the `[Unreleased]` section in `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added

- New feature description (#PR_NUMBER)

### Changed

- Modified behavior description (#PR_NUMBER)

### Fixed

- Bug fix description (#PR_NUMBER)
```

Categories: **Added**, **Changed**, **Deprecated**, **Removed**, **Fixed**, **Security**

## Issue Reporting

### Creating Issues

When creating an issue, please use the appropriate issue template:

- **[Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml)** - Report bugs or unexpected behavior
- **[Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml)** - Suggest new features or enhancements
- **[Documentation](.github/ISSUE_TEMPLATE/documentation.yml)** - Suggest documentation improvements

The templates will guide you through providing all necessary information.

### Before Creating an Issue

- Search existing issues to avoid duplicates
- Check if your issue is already fixed in the latest version
- Gather relevant information (version, platform, error messages)

### Bug Reports

When reporting bugs, the template will ask for:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, changes-roller version)
- Error messages and stack traces
- Configuration files (if relevant)

### Feature Requests

When requesting features, the template will ask for:

- Clear description of the desired functionality
- Use cases and motivation
- Proposed implementation approach
- Impact on your workflow
- Willingness to contribute

### Questions and Discussions

For questions about usage:

- Check the README and documentation first
- Search closed issues for similar questions
- Open a [GitHub Discussion](https://github.com/k-pavlo/changes-roller/discussions)
- For security issues, see [SECURITY.md](SECURITY.md)

## Development Workflow Summary

```bash
# 1. Set up environment
git clone https://github.com/YOUR-USERNAME/changes-roller.git
cd changes-roller
python -m venv venv
source venv/bin/activate
pip install -e ".[dev,test]"
pre-commit install
pre-commit install --hook-type commit-msg

# 2. Create branch
git checkout -b feature/my-feature

# 3. Make changes and test
# Edit code...
pytest  # Run tests

# 4. Commit and push
git add .
git commit -m "feat: description of changes"
# Pre-commit hooks run automatically here!
# If hooks fail, fix issues and commit again
git push origin feature/my-feature

# 5. Open Pull Request on GitHub
```

**Note:** Pre-commit hooks automatically check code quality before commits. Manual checks are optional.

## Questions?

If you have questions about contributing, feel free to:

- Open a GitHub Discussion
- Open an issue with the question label
- Contact the maintainers (see CODE_OF_CONDUCT.md)

Thank you for contributing to changes-roller!
