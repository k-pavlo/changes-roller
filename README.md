# changes-roller

[![PyPI version](https://badge.fury.io/py/changes-roller.svg)](https://badge.fury.io/py/changes-roller)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Stop manually patching dozens of repositories. Automate it.**

**Changes-Roller** is a command-line tool for creating and managing coordinated
patch series across multiple Git repositories simultaneously.

## Why changes-roller?

It's Tuesday morning, and you've just discovered a critical security vulnerability affecting 47 of your repositories. You know what comes next: hours of manual cloning, editing, committing, and reviewing. Your afternoon vanishes into mechanical `git clone`, `git commit`, `git review` while your actual development work waits.

changes-roller transforms this soul-crushing routine into a five-minute automation. Write your patch script once, then watch as it executes across all repositories in parallel. What used to consume your entire afternoon now runs while you grab coffee—with consistent changes, uniform commit messages, and organized code reviews.

**Perfect for:**
- Security updates across multiple microservices
- Dependency upgrades throughout your service ecosystem
- API migrations affecting client libraries
- License header updates for compliance
- Configuration file standardization
- Any scenario requiring identical changes across multiple repositories

## How It Works

Configure once, execute everywhere. You provide the repositories to update and a script containing your changes. changes-roller handles everything else—cloning, patching, testing, committing, and submitting for review. Parallel execution means 50 repositories finish almost as quickly as one. Built-in error handling ensures you get clear feedback about any issues, while successful repositories continue processing.

## Features

- Apply patches to multiple Git repositories in parallel
- Custom patch scripts with full repository access
- Automated Git operations (clone, commit, stage)
- **Git branch switching** - Apply changes to specific branches (e.g., stable branches)
- **Custom command execution** - Run commands before/after applying changes
- **Dry-run mode** - Preview operations without executing them
- Automatic commit sign-off (Signed-off-by line)
- Automatic git-review setup for Gerrit integration
- Commit message templating with variables
- Gerrit code review integration with topic grouping
- Optional test execution before committing (e.g., `tox -e pep8`)
- Clear progress reporting and error handling

## Installation

```bash
# Install in development mode
pip install -e .

# Or install from source
pip install .
```

## Requirements

- Python 3.12 or higher
- Git command-line client
- git-review (optional, for Gerrit integration)

## Quick Start

1. Generate a configuration file:
```bash
roller init --output my-series.ini
```

2. Create a patch script (`my_patch.sh`):
```bash
#!/bin/bash
# Example: Update a dependency version
sed -i 's/old-library==1.0/old-library==2.0/' requirements.txt
chmod +x my_patch.sh
```

3. Edit the configuration file to specify your repositories and patch script:
```bash
nano my-series.ini
# Update the 'projects' list and 'commands' path
```

4. Run the patch series:
```bash
roller create --config-file my-series.ini
```

## Configuration

### [SERIE] Section

**Basic Options:**
- `projects` (required): Comma-separated list of Git repository URLs
- `commands` (required): Path to executable patch script
- `commit_msg` (required): Commit message template (supports `{{ project_name }}`)
- `topic` (optional): Code review topic name
- `commit` (optional): Enable automatic commits (default: true)
- `review` (optional): Enable Gerrit review submission (default: false)

**Branch Switching Options:**
- `branch` (optional): Target branch to switch to before applying changes
- `create_branch` (optional): Create branch if it doesn't exist (default: false)
- `stay_on_branch` (optional): Don't return to original branch after completion (default: false)

**Command Execution Options:**
- `pre_commands` (optional): Commands to run before applying changes (one per line)
- `post_commands` (optional): Commands to run after committing (one per line)
- `continue_on_error` (optional): Continue if commands fail (default: false)
- `dry_run` (optional): Preview operations without executing (default: false)

### [TESTS] Section

- `run` (optional): Enable test execution (default: false)
- `blocking` (optional): Fail if tests fail (default: false)
- `command` (optional): Test command to run (default: tox)

Example: `command = tox -e pep8` runs PEP8 checks before committing

## Command-Line Options

### roller init

Generate a template configuration file.

```bash
roller init [options]

Options:
  -o, --output PATH    Output file path (default: series.ini)
  -f, --force          Overwrite existing file
  --help               Show help message
```

### roller create

Create a new patch series across multiple repositories.

```bash
roller create --config-file <path> [options]

Options:
  --config-file PATH        Path to configuration file (required)
  --config-dir PATH         Additional directory for config files
  -e, --exit-on-error       Exit immediately on first failure
  -v, --verbose             Enable verbose output

  # Branch switching
  --branch NAME             Target branch to switch to before applying changes
  --create-branch           Create branch if it doesn't exist (requires --branch)
  --stay-on-branch          Don't return to original branch after completion

  # Command execution
  --pre-command CMD         Command to execute before changes (repeatable)
  --post-command CMD        Command to execute after changes (repeatable)
  --continue-on-error       Continue if commands fail instead of stopping
  --dry-run                 Preview operations without executing them

  --help                    Show help message
```

## Examples

### Basic Usage

```bash
# Apply patch to multiple repositories
roller create --config-file my-series.ini
```

### Branch Switching

```bash
# Apply changes to a specific branch
roller create --config-file security-fix.ini --branch stable/2024.2

# Multi-branch backport
for branch in stable/2024.1 stable/2024.2 stable/2025.1; do
  roller create --config-file fix.ini --branch $branch
done
```

### With Commands

```bash
# Pull latest before patching, push after committing
roller create --config-file series.ini \
  --pre-command "git pull origin main" \
  --post-command "git push origin main"

# Validate before and after
roller create --config-file series.ini \
  --pre-command "pytest tests/" \
  --post-command "git push"
```

### Dry Run

```bash
# Preview what would happen without executing
roller create --config-file series.ini --dry-run
```

### With Testing

Configuration file with PEP8 validation:

```ini
[SERIE]
projects = https://github.com/org/repo1,
           https://github.com/org/repo2
commands = ./my-patch.sh
commit_msg = Fix styling in {{ project_name }}

[TESTS]
run = true
blocking = true
command = tox -e pep8
```

### More Examples

See the `examples/` directory for complete examples:

- `examples/dependency-update/` - Update a dependency across repos
- `examples/license-headers/` - Add license headers to source files
- `examples/config-migration/` - Migrate configuration files

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format .

# Linting
ruff check .

# Type checking
mypy roller/
```

## Contributing

We welcome contributions! Please see our contributing guidelines and community standards:

- **[Contributing Guide](CONTRIBUTING.md)** - Development setup, code standards, and PR process
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community standards and expectations
- **[Changelog](CHANGELOG.md)** - Release history and version changes
- **[Security Policy](SECURITY.md)** - Reporting issues and safe usage guidelines

## License

See LICENSE file for details.
