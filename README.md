# changes-roller

A command-line tool for creating and managing coordinated patch series across multiple Git repositories simultaneously.

## Overview

changes-roller automates the workflow of applying consistent changes to many projects and optionally submitting them for code review. It's perfect for:

- Security updates across multiple microservices
- Dependency upgrades
- API migrations
- License header updates
- Compliance fixes

## Features

- Apply patches to multiple Git repositories in parallel
- Custom patch scripts with full repository access
- Automated Git operations (clone, commit, stage)
- Automatic commit sign-off (Signed-off-by line)
- Automatic git-review setup for Gerrit integration
- Commit message templating with variables
- Gerrit code review integration with topic grouping
- Optional test execution before committing
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

- `projects` (required): Comma-separated list of Git repository URLs
- `commands` (required): Path to executable patch script
- `commit_msg` (required): Commit message template (supports `{{ project_name }}`)
- `topic` (optional): Code review topic name
- `commit` (optional): Enable automatic commits (default: true)
- `review` (optional): Enable Gerrit review submission (default: false)

### [TESTS] Section

- `run` (optional): Enable test execution (default: false)
- `blocking` (optional): Fail if tests fail (default: false)
- `command` (optional): Test command to run (default: tox)

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
  --config-file PATH    Path to configuration file (required)
  --config-dir PATH     Additional directory for config files
  -e, --exit-on-error  Exit immediately on first failure
  -v, --verbose        Enable verbose output
  --help               Show help message
```

## Examples

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
black roller/

# Type checking
mypy roller/
```

## License

See LICENSE file for details.