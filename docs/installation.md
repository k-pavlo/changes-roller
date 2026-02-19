# Installation

```{include} ../README.md
:start-after: "## Requirements"
:end-before: "## Quick Start"
```

## Installing from PyPI

```bash
pip install changes-roller
```

## Installing from Source

### Development Installation

For development work or to get the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/k-pavlo/changes-roller.git
cd changes-roller

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/k-pavlo/changes-roller.git
cd changes-roller

# Install
pip install .
```

## Verify Installation

```bash
# Check that roller is available
roller --version

# Get help
roller --help
```

## Optional Dependencies

### Development Tools

If you plan to contribute to changes-roller, install the development dependencies:

```bash
pip install -e ".[dev]"
```

This includes:

- ruff (linting and formatting)
- mypy (type checking)
- bandit (security scanning)
- pre-commit (git hooks)

### Testing Tools

To run the test suite:

```bash
pip install -e ".[test]"
```

This includes:

- pytest (testing framework)
- pytest-cov (coverage reporting)
- pytest-mock (mocking utilities)

### Documentation Tools

To build documentation locally:

```bash
pip install -e ".[docs]"
```

This includes:

- sphinx (documentation generator)
- furo (documentation theme)
- sphinx-autoapi (API documentation)
- myst-parser (Markdown support)

### Gerrit Integration

For Gerrit code review integration, install git-review:

```bash
pip install git-review
```

Or on Ubuntu/Debian:

```bash
sudo apt-get install git-review
```

## Troubleshooting

### Command Not Found

If `roller` is not found after installation, ensure your Python scripts directory is in your PATH:

```bash
# Linux/macOS
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.bashrc or ~/.zshrc to make permanent
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Permission Denied

If you get permission errors during installation:

```bash
# Install to user directory instead of system-wide
pip install --user changes-roller
```

### Python Version Issues

Verify you have Python 3.10 or higher:

```bash
python3 --version
```

If you have multiple Python versions, specify the correct one:

```bash
python3 -m pip install changes-roller
```
