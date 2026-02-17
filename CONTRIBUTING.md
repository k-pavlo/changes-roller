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

## Continuous Integration

This project uses GitHub Actions for automated testing and quality checks on every pull request.

### What CI Checks

Every pull request automatically runs the following checks:

#### 1. Code Quality (~2 min)

Runs first to provide fast feedback:

- **Ruff formatting** - Code formatting check
- **Ruff linting** - Code quality and style check
- **File validation** - Trailing whitespace, EOF, YAML/TOML syntax
- **Prettier** - Markdown and JSON formatting

These match the pre-commit hooks, so if pre-commit passes locally, this will pass in CI.

#### 2. Type Checking (~2 min)

Runs in parallel with code quality:

- **MyPy** - Strict static type checking on Python 3.10
- Ensures type safety across the codebase

#### 3. Tests (~5-10 min)

Runs after quality checks pass:

- **128 tests** across 7 test files
- **Multi-Python**: 3.10, 3.11, 3.12, 3.13
- **Multi-OS**: Ubuntu, macOS, Windows
- **Coverage reporting** - Uploaded to Codecov
- **8 parallel test jobs** for comprehensive compatibility testing

#### 4. Security Scanning (~2-3 min)

- **Bandit** - Python code security issues
- **pip-audit** - Dependency vulnerabilities (warning only)
- **Dependency Review** - Blocks PRs introducing vulnerable dependencies

### CI Workflow

1. **Push commits** to your PR branch
2. **CI automatically runs** all checks
3. **Review results** in PR (status checks appear at bottom)
4. **Fix failures** if any and push again
5. **All checks must pass** before merging

### Viewing CI Results

**In your PR:**

- Scroll to bottom of PR page
- Status checks appear with ✓ (pass) or ✗ (fail)
- Click "Details" next to any check to view logs

**In Actions tab:**

- Navigate to repository → Actions
- Click on your workflow run
- View detailed logs for each job

### Troubleshooting CI Failures

#### "lint-and-format" failed

Most common causes:

- Code formatting issues
- Linting errors
- Invalid YAML/TOML syntax

**Fix locally:**

```bash
# Run pre-commit to see all issues
pre-commit run --all-files

# Auto-fix formatting
ruff format .
ruff check --fix .

# Fix any remaining issues manually
```

#### "type-check" failed

Type errors in the code.

**Fix locally:**

```bash
# Run MyPy to see errors
mypy roller/

# Fix type errors
# - Add type hints where missing
# - Fix incorrect type annotations
# - Use proper type guards
```

#### "test" failed

Test failures or errors.

**Fix locally:**

```bash
# Run tests to see failures
pytest

# Run specific failing test with verbose output
pytest tests/test_cli.py::test_specific_function -v

# Run with debugger
pytest --pdb

# Check coverage
pytest --cov=roller --cov-report=term-missing
```

#### "bandit" (security) failed

Security issues detected in code.

**Fix locally:**

```bash
# Run Bandit to see issues
bandit -c pyproject.toml -r roller/

# Fix security issues
# - Avoid shell=True in subprocess calls
# - Validate user input
# - Use secure random instead of random
# - Don't hardcode secrets

# If false positive, add comment:
# nosec: B603 - subprocess call is safe here
```

### Local Pre-commit vs CI

**Pre-commit hooks** (local):

- Run **before commit** on changed files
- Catch issues early before pushing
- Fast feedback (~10-30 seconds)
- Auto-fix many issues

**CI checks** (GitHub Actions):

- Run **on GitHub** on all files
- Ensure comprehensive cross-platform testing
- Slower but thorough (~10-15 minutes)
- Required for merge

**Best practice:**

- Always let pre-commit hooks run (don't use `--no-verify`)
- Pre-commit catches most issues before CI
- CI provides comprehensive multi-platform validation

### CI Performance

**Expected times:**

- Fast feedback (lint + type): ~2-4 minutes
- Full test matrix: ~5-10 minutes
- Security scans: ~2-3 minutes
- **Total**: ~10-15 minutes for complete validation

**Optimizations in place:**

- Path ignore for docs-only changes
- Caching for dependencies and tools
- Parallel job execution
- Reduced matrix for macOS/Windows

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

## Documentation

We use Sphinx to generate documentation hosted on ReadTheDocs.

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build HTML documentation
cd docs
sphinx-build -b html . _build/html

# View documentation
# Open docs/_build/html/index.html in your browser
```

### Documentation Structure

- `docs/` - Sphinx documentation source files
- `docs/conf.py` - Sphinx configuration
- `docs/index.rst` - Main documentation index
- `docs/*.md` - Documentation pages (Markdown format)
- `.readthedocs.yaml` - ReadTheDocs configuration

### Writing Documentation

- Use Markdown (`.md`) for most documentation pages
- Follow the existing structure and style
- Include code examples where appropriate
- Update relevant docs when adding features or changing behavior
- Test documentation builds locally before submitting

### ReadTheDocs Integration

- Documentation builds automatically on every commit to main
- View live documentation at: https://changes-roller.readthedocs.io
- Documentation for pull requests is built as preview versions
- Build status is visible in PR checks

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

### Automated Version Bumping

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) for automated semantic versioning.

#### How Version Bumping Works

Version numbers are automatically calculated from your commit messages:

- `feat:` commits → MINOR version bump (0.1.0 → 0.2.0)
- `fix:` commits → PATCH version bump (0.1.0 → 0.1.1)
- `BREAKING CHANGE:` in commit footer → MAJOR version bump (0.1.0 → 1.0.0)
- Other commit types (docs, style, etc.) → No version bump

#### Bumping a New Version

**Maintainers only** - Contributors don't need to bump versions.

```bash
# 1. Ensure all changes are committed
git status

# 2. Preview the version bump (dry run)
cz bump --dry-run

# 3. Bump the version
cz bump

# This automatically:
# - Determines version increment from commits
# - Updates version in pyproject.toml and roller/__init__.py
# - Updates CHANGELOG.md with release notes
# - Creates a git commit and tag
# - Does NOT push (you control when to push)

# 4. Review the changes
git log -1 --stat
git show HEAD

# 5. Push the release
git push
git push --tags
```

#### Manual Override

Force a specific version increment if needed:

```bash
cz bump --increment MAJOR   # Force major version bump
cz bump --increment MINOR   # Force minor version bump
cz bump --increment PATCH   # Force patch version bump
```

#### Troubleshooting

**"No commits found to bump version"**

- No commits with feat/fix/BREAKING CHANGE since last version
- Solution: This is expected; version only bumps when there's new functionality or fixes

**"Version file not found"**

- Ensure version format matches: `version = "X.Y.Z"` and `__version__ = "X.Y.Z"`

## Release Process

This project uses automated PyPI publishing via GitHub Actions with **Trusted Publishers** (OIDC) - a secure, token-free authentication method.

### How Releases Work

When a version tag is pushed to GitHub, an automated workflow:

1. **Builds** the package using hatchling
2. **Publishes** to PyPI using secure OIDC authentication (no API tokens needed)
3. **Creates** a GitHub Release with auto-generated release notes
4. **Attaches** distribution files to the release

### Creating a Release

**Maintainers only** - This process is for project maintainers.

#### Step 1: Ensure Main Branch is Ready

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Verify everything is clean
git status

# Run all quality checks
pre-commit run --all-files
pytest
```

#### Step 2: Bump Version with Commitizen

```bash
# Preview the version bump
cz bump --dry-run

# Bump the version (creates commit and tag)
cz bump

# Review the changes
git log -1 --stat
git show HEAD
```

This automatically:

- Calculates version from conventional commits
- Updates `pyproject.toml` and `roller/__init__.py`
- Updates `CHANGELOG.md` with release notes
- Creates a git commit with the changes
- Creates a version tag (e.g., `v0.2.0`)

#### Step 3: Push to Trigger Release

```bash
# Push the version bump commit
git push origin main

# Push the version tag (this triggers the release workflow)
git push origin --tags
```

#### Step 4: Monitor Release Workflow

1. Navigate to **Actions** tab on GitHub
2. Watch the **Release to PyPI** workflow
3. Verify all jobs succeed:
   - ✅ Build distribution packages
   - ✅ Publish to PyPI
   - ✅ Create GitHub Release

#### Step 5: Verify Release

**Check PyPI:**

- Visit: https://pypi.org/project/changes-roller/
- Verify new version is published
- Test installation: `pip install changes-roller==<version>`

**Check GitHub Release:**

- Visit: https://github.com/k-pavlo/changes-roller/releases
- Verify release is created with proper notes
- Check that distribution files are attached

### Trusted Publishers (OIDC)

This project uses **Trusted Publishers** for secure PyPI authentication:

#### What is Trusted Publishing?

- **Token-free authentication** using OpenID Connect (OIDC)
- GitHub Actions authenticates directly with PyPI
- No long-lived API tokens to manage or secure
- Scoped to specific repository and workflow
- PyPI's recommended approach for automated publishing

#### Security Benefits

✅ **No secrets stored** in GitHub repository
✅ **Automatic token rotation** via OIDC
✅ **Scoped permissions** to specific repo/workflow
✅ **Audit trail** of all publishing events
✅ **Cannot be leaked** - tokens are ephemeral

#### Configuration

**On PyPI** (already configured):

1. Go to project settings: https://pypi.org/manage/project/changes-roller/settings/
2. Navigate to "Publishing" tab
3. Trusted publisher configured with:
   - Owner: `k-pavlo`
   - Repository: `changes-roller`
   - Workflow: `release.yml`
   - Environment: `release`

**In GitHub** (workflow permissions):

```yaml
permissions:
  id-token: write # Required for OIDC authentication
```

### Release Workflow Details

The `.github/workflows/release.yml` workflow includes three jobs:

#### 1. Build (runs on all platforms)

- Checks out code
- Sets up Python 3.12
- Builds wheel and source distribution with hatchling
- Uploads artifacts for publishing

#### 2. Publish to PyPI (runs after build)

- Downloads built distributions
- Authenticates via OIDC (no token needed)
- Publishes to PyPI using `pypa/gh-action-pypi-publish`
- Uses `release` environment for protection

#### 3. Create GitHub Release (runs after publish)

- Creates GitHub Release from tag
- Auto-generates release notes from commits
- Attaches distribution files
- Links to PyPI package page

### Hotfix Releases

For urgent bug fixes:

```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/critical-fix main

# 2. Make minimal fixes
# ... edit code ...

# 3. Commit with conventional commit message
git commit -m "fix: resolve critical security vulnerability"

# 4. Merge to main
git checkout main
git merge hotfix/critical-fix

# 5. Bump version (will be PATCH increment)
cz bump

# 6. Push to release
git push origin main
git push origin --tags
```

### Rollback Strategy

If a release has issues:

#### Option 1: Yank Release (PyPI)

```bash
# Yank the problematic version on PyPI
# This prevents new installations but doesn't break existing ones
# Must be done manually via PyPI web interface
```

1. Go to https://pypi.org/manage/project/changes-roller/releases/
2. Find the problematic version
3. Click "Options" → "Yank release"
4. Provide reason for yanking

#### Option 2: Release Fix Immediately

```bash
# 1. Fix the issue on main
git commit -m "fix: resolve regression in v0.2.0"

# 2. Bump version (PATCH increment)
cz bump

# 3. Push to release
git push origin main
git push origin --tags
```

### Troubleshooting Releases

#### "Trusted publisher validation failed"

**Cause:** OIDC configuration mismatch between PyPI and GitHub workflow.

**Solution:**

1. Verify PyPI trusted publisher settings match workflow
2. Ensure workflow uses `release` environment
3. Check that workflow has `id-token: write` permission

#### "Package already exists on PyPI"

**Cause:** Trying to re-upload same version.

**Solution:**

1. PyPI doesn't allow re-uploading same version
2. Bump to new version and release again
3. If needed, yank the old version on PyPI

#### "Build failed"

**Cause:** Package build error with hatchling.

**Solution:**

```bash
# Test build locally
pip install --upgrade build hatchling
python -m build

# Fix any build errors
# Commit fixes and push
```

#### "GitHub Release creation failed"

**Cause:** Workflow lacks permissions or tag already has release.

**Solution:**

1. Check workflow has `contents: write` permission
2. Delete existing release if re-creating
3. Re-run workflow from Actions tab

### Pre-release Versions

For testing before official release:

```bash
# Manually create pre-release version
# Edit version in pyproject.toml and roller/__init__.py to:
# version = "0.2.0rc1"  # Release candidate

# Commit and tag
git commit -m "chore: prepare release candidate 0.2.0rc1"
git tag v0.2.0rc1
git push origin main --tags

# This publishes to PyPI as pre-release
# Users can install with: pip install --pre changes-roller
```

### Release Checklist

Before creating a release:

- [ ] All tests passing in CI
- [ ] CHANGELOG.md updated (done automatically by `cz bump`)
- [ ] Version bumped with `cz bump`
- [ ] Tag created and pushed
- [ ] GitHub Actions workflow succeeded
- [ ] PyPI package published and installable
- [ ] GitHub Release created
- [ ] Documentation updated (if needed)
- [ ] Announcement drafted (if major release)

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
