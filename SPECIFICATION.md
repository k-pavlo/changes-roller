# changes-roller Tool Specification

## Executive Summary

changes-roller is a command-line tool for creating and managing coordinated patch series across multiple Git repositories simultaneously. It automates the workflow of applying consistent changes to many projects and optionally submitting them for code review.

## Problem Statement

Software organizations often need to apply the same changes across multiple related projects—such as security updates, dependency upgrades, API migrations, or compliance fixes. Doing this manually for dozens of repositories is:

- **Time-consuming**: Cloning, patching, committing, and submitting each project individually
- **Error-prone**: Risk of inconsistent changes or missing repositories
- **Tedious**: Repetitive tasks that could be automated
- **Hard to track**: Difficult to maintain overview of progress across all projects

## Goals and Objectives

### Primary Goals
1. Enable bulk patching of multiple Git repositories from a single command
2. Automate repetitive Git operations (clone, commit, stage)
3. Ensure consistency of changes and commit messages across all projects
4. Integrate with existing workflows (testing, code review)
5. Provide clear feedback on success/failure for each repository

### Non-Goals
- Not a version control system replacement
- Not a patch management system for tracking patch state over time
- Not a code review platform (integrates with existing ones)

## Feature Requirements

### 1. Multi-Repository Management

**Requirement**: Support patching an arbitrary number of Git repositories in a single execution.

**Details**:
- User provides a list of Git repository URLs
- Tool clones each repository to a temporary workspace
- Each repository is processed independently
- Failures in one repository should not block others (unless user specifies fail-fast mode)

### 2. Custom Patch Scripts

**Requirement**: Allow users to define arbitrary change logic via shell scripts.

**Details**:
- User provides a path to an executable script
- Script is executed in the context of each cloned repository
- Script has full access to repository files and can make any changes
- Script exit codes determine success/failure

**Use Cases**:
- Find-and-replace operations (sed, awk)
- File additions or deletions
- Code generation or template updates
- Running formatters or linters
- Any file system operation

### 3. Automated Git Operations

**Requirement**: Automatically handle Git operations for modified repositories.

**Details**:
- Detect changes made by the patch script (git status)
- Stage all changes (git add)
- Create commits with user-specified messages
- Skip repositories with no changes
- Optionally submit changes to remote code review system

### 4. Commit Message Templating

**Requirement**: Support dynamic commit messages with variable substitution.

**Details**:
- Allow template variables in commit messages (e.g., `{{ project_name }}`)
- Substitute variables at runtime for each repository
- Support multi-line commit messages

**Example**:
```
Update dependencies in {{ project_name }}

Bump hacking library to version 4.0.0 for improved Python 3.9 support.
```

### 5. Code Review Integration

**Requirement**: Integrate with Gerrit (or similar code review systems).

**Details**:
- Support assigning topics to group related patches
- Submit patches for review with a single command
- Allow dry-run mode (commit locally but don't submit)
- Track which repositories were successfully submitted

### 6. Testing Integration

**Requirement**: Optionally run tests before committing or submitting patches.

**Details**:
- Support running test frameworks (tox, pytest, etc.)
- Configurable test execution per series
- Blocking mode: fail the patch if tests fail
- Non-blocking mode: warn but continue if tests fail

### 7. Configuration Management

**Requirement**: Use configuration files to define patch series.

**Details**:
- Support standard configuration file formats (INI, YAML, or similar)
- Allow configuration via file and/or command-line arguments
- Configuration should be reusable and version-controllable

**Required Configuration Options**:
- `projects`: List of Git repository URLs or paths
- `commands`: Path to patch script file
- `commit_msg`: Commit message template
- `topic`: Code review topic name (optional)
- `commit`: Enable/disable automatic commits (boolean)
- `review`: Enable/disable review submission (boolean)
- Testing options:
  - `run_tests`: Enable/disable test execution (boolean)
  - `tests_blocking`: Whether test failures should block patching (boolean)

### 8. Error Handling and Reporting

**Requirement**: Provide clear feedback and handle failures gracefully.

**Details**:
- Display progress for each repository being processed
- Report success/failure status for each operation
- Support fail-fast mode (exit on first error)
- Support fail-safe mode (continue processing remaining repos after errors)
- Log errors with sufficient detail for debugging

### 9. Workspace Management

**Requirement**: Manage temporary workspaces for cloning and patching.

**Details**:
- Create isolated workspace directories for each series execution
- Prevent conflicts between concurrent executions
- Optionally clean up workspace after completion
- Allow user to inspect workspace for debugging

## User Interaction Model

### Command-Line Interface

The tool should expose a CLI with the following structure:

```
roller <command> [options]
```

### Commands

#### `create`
Create a new patch series across multiple repositories.

**Usage**:
```bash
roller create --config-file <path> [--exit-on-error]
```

**Options**:
- `--config-file <path>`: Path to configuration file (required)
- `--config-dir <path>`: Additional directory for config files (optional)
- `-e, --exit-on-error`: Exit immediately on first failure (optional)

**Behavior**:
1. Read configuration file
2. Create temporary workspace
3. For each project:
   - Clone repository
   - Execute patch script
   - Check for changes
   - Run tests (if enabled)
   - Commit changes (if enabled and changes exist)
   - Submit for review (if enabled)
4. Display summary of results

#### `update` (Future)
Update an existing patch series (e.g., after code review feedback).

**Usage**:
```bash
roller update --config-file <path>
```

**Behavior**:
- Locate existing workspace or clones
- Re-apply updated patch script
- Amend commits or create new commits
- Re-submit for review

### Configuration File Format

Configuration files should use INI format with the following sections:

```ini
[SERIE]
projects = https://github.com/org/repo1,
           https://github.com/org/repo2,
           https://github.com/org/repo3
commands = /path/to/patch_script.sh
commit_msg = Update dependencies in {{ project_name }}

             Detailed description of changes.
topic = dependency-updates-2025
commit = true
review = false

[TESTS]
run = true
blocking = true
```

### Output Format

The tool should provide clear, structured output:

```
Starting patch series: dependency-updates-2025
Workspace: /tmp/changes-roller-abc123

[1/3] Processing repo1...
  ✓ Cloned repository
  ✓ Executed patch script
  ✓ Running tests... PASSED
  ✓ Committed changes (abc123f)

[2/3] Processing repo2...
  ✓ Cloned repository
  ✓ Executed patch script
  ℹ No changes detected, skipping

[3/3] Processing repo3...
  ✓ Cloned repository
  ✗ Patch script failed (exit code 1)

Summary:
  Succeeded: 1
  Skipped: 1
  Failed: 1
```

## Workflow Specification

### Typical Workflow

1. **Prepare Patch Script**
   - User creates a shell script containing the changes to apply
   - Script should be idempotent (safe to run multiple times)

2. **Create Configuration**
   - User creates a configuration file listing target repositories
   - Defines commit message, topic, and options

3. **Execute Patch Series**
   - Run `roller create --config-file config.ini`
   - Tool processes each repository sequentially or in parallel

4. **Review Results**
   - Check output for any failures
   - Inspect workspace if needed for debugging

5. **Submit for Review** (Optional)
   - If review mode enabled, patches are automatically submitted
   - Otherwise, user can manually push or submit from workspace

6. **Update if Needed** (Future)
   - After code review feedback, update patch script
   - Run `roller update --config-file config.ini`

### Error Recovery Workflow

1. **Identify Failed Repositories**
   - Review execution summary
   - Check logs for error details

2. **Fix Issues**
   - Update patch script to handle edge cases
   - Manually fix problematic repositories if needed

3. **Re-run Series**
   - Run create command again (should be idempotent)
   - Or create new config with only failed repositories

## Technical Requirements

### Platform Support
- Linux
- Python 3.12 or higher

### Dependencies
- Git command-line client must be installed
- Install click to manage appealing CLI
- Test framework (tox, pytest, etc.) if testing enabled
- Gerrit CLI tools if review submission enabled

### Performance Considerations
- Should handle 50+ repositories efficiently
- Consider parallel processing for independent operations
- Provide progress indicators for long-running operations

### Security Considerations
- Never store credentials in configuration files
- Use SSH keys or credential managers for Git authentication
- Validate and sanitize user-provided scripts before execution
- Isolate execution environments to prevent script interference

## Success Criteria

A successful implementation should:

1. **Functional Completeness**
   - Execute patch scripts across multiple repositories
   - Create commits with templated messages
   - Integrate with testing frameworks
   - Support code review submission

2. **Reliability**
   - Handle errors gracefully without corrupting repositories
   - Provide accurate status reporting
   - Support recovery from partial failures

3. **Usability**
   - Clear, intuitive command-line interface
   - Helpful error messages
   - Good documentation and examples

4. **Performance**
   - Complete patching of 20 repositories in under 5 minutes (assuming fast network)
   - Minimal resource usage
   - Responsive output during execution

5. **Maintainability**
   - Clean, well-documented code
   - Modular architecture for easy extension
   - Comprehensive test coverage

## Future Enhancements (Optional)

- Support for additional VCS systems (GitHub PRs, GitLab MRs)
- Parallel processing of repositories
- Web UI for monitoring progress
- Patch series state persistence and resumption
- Integration with CI/CD pipelines
- Dry-run mode to preview changes without committing
- Selective repository targeting (filters, patterns)
- Change rollback capabilities

## Appendix: Example Use Cases

### Use Case 1: Security Dependency Update
Update a vulnerable library across all microservices:
- 30 microservice repositories
- Patch script updates requirements.txt
- Run tests to ensure compatibility
- Submit all patches with topic "CVE-2025-1234-fix"

### Use Case 2: License Header Update
Add or update license headers in all projects:
- 50+ library repositories
- Patch script adds SPDX headers to source files
- Skip projects that already have headers
- Commit without code review (internal compliance)

### Use Case 3: API Migration
Migrate from deprecated API to new version:
- 15 client libraries
- Patch script runs find-replace for API methods
- Run extensive test suite (blocking)
- Submit for manual code review before merge
