# Project Safety Policy

## Supported Versions

We release patches for issues affecting the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting Issues

If you discover a concern with this project, please report it responsibly.

### How to Report

Please send details to: **pasha.k460@gmail.com**

Include in your report:
- Description of the concern
- Steps to reproduce the issue
- Affected versions
- Any potential mitigations you've identified

### Response Timeline

- **Initial Response**: Within 48 hours of receiving your report
- **Status Update**: Within 7 days with our assessment
- **Resolution**: Timeline depends on complexity and severity

### What to Expect

1. We will acknowledge receipt of your report
2. We will investigate and assess the impact
3. We will work on a fix and coordinate disclosure
4. We will credit you in the release notes (if desired)

## Safe Usage Guidelines

When using changes-roller:

- **Review configuration files** before execution
- **Use dry-run mode** (`--dry-run`) to preview operations
- **Validate patch scripts** before applying to production repositories
- **Limit repository access** using appropriate Git credentials
- **Test changes** in non-production environments first
- **Be cautious with custom commands** (`--pre-command`, `--post-command`)

## Known Considerations

### Command Execution

This tool executes shell commands as part of its core functionality:
- Patch scripts specified in configuration
- Git operations on repositories
- Optional pre/post commands
- Optional test commands

**Important**: Only use trusted configuration files and patch scripts. Review all commands before execution.

### Git Credentials

The tool uses your system's Git configuration and credentials. Ensure:
- Git credentials are properly secured
- Repository access is appropriately scoped
- SSH keys or tokens follow your organization's policies

## Questions?

For general questions about safe usage, please open a GitHub issue or discussion.
