# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Community standard files (CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md)
- This CHANGELOG.md following Keep a Changelog format

## [0.1.0] - 2026-02-11

### Added
- CLI tool for coordinated patch series across multiple repositories
- `roller init` command for generating configuration templates
- `roller create` command for applying patches to multiple repositories
- Support for parallel processing with configurable concurrency
- Git branch switching capabilities (`--branch`, `--create-branch`, `--stay-on-branch`)
- Custom command execution (`--pre-command`, `--post-command`)
- Dry-run mode for previewing operations without execution
- Automatic commit sign-off (Signed-off-by line)
- Automatic git-review setup for Gerrit integration
- Commit message templating with variables (e.g., `{{ project_name }}`)
- Gerrit code review integration with topic grouping
- Optional test execution before committing
- Comprehensive test suite with >90% code coverage
- Code quality tools (Ruff for linting/formatting, MyPy for type checking, Bandit for security)
- Rich PyPI metadata with project URLs and classifiers
- MIT License
- Comprehensive documentation (README.md, SPECIFICATION.md, USAGE.md)
- Example workflows for common use cases

### Configuration Options
- Support for INI-based configuration files
- `[SERIE]` section for patch series configuration
- `[TESTS]` section for test execution configuration
- Branch switching options in configuration
- Pre/post command execution in configuration

[unreleased]: https://github.com/k-pavlo/changes-roller/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/k-pavlo/changes-roller/releases/tag/v0.1.0
