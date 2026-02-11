# Usage Guide

This guide provides detailed instructions on using changes-roller.

## Installation

```bash
# Install the tool
pip install -e .

# Verify installation
roller --version
```

## Basic Workflow

### 1. Generate a Configuration Template (Optional but Recommended)

Use the `init` command to generate a template configuration file:

```bash
# Create with default name (series.ini)
roller init

# Or specify a custom name
roller init --output my-series.ini

# Overwrite existing file
roller init --force
```

This creates a fully documented template with all available options.

### 2. Create a Patch Script

Create an executable shell script that performs your desired changes:

```bash
#!/bin/bash
# Example: patch.sh

# Your patch logic here
# The script runs in the context of each cloned repository
# Exit with non-zero code on failure

# Example: Update a configuration file
sed -i 's/old_value/new_value/g' config.yml
```

Make it executable:
```bash
chmod +x patch.sh
```

### 3. Edit the Configuration File

If you used `roller init`, edit the generated file. Otherwise, create an INI configuration file (`series.ini`):

```ini
[SERIE]
# Comma-separated list of repository URLs
projects = https://github.com/org/repo1,
           https://github.com/org/repo2

# Path to your patch script
commands = ./patch.sh

# Commit message template
# Use {{ project_name }} for the repository name
commit_msg = Update configuration in {{ project_name }}

             This updates the configuration from old_value to new_value
             for improved performance.

# Optional: Gerrit topic for grouping patches
topic = config-update-2025

# Create commits (default: true)
commit = true

# Submit to Gerrit for review (default: false)
review = false

[TESTS]
# Run tests before committing (default: false)
run = false

# Fail if tests fail (default: false)
blocking = false

# Test command to execute (default: tox)
command = tox
```

### 4. Execute the Patch Series

```bash
# Basic execution
roller create --config-file series.ini

# Exit on first error
roller create --config-file series.ini --exit-on-error

# Verbose output
roller create --config-file series.ini --verbose
```

## Configuration Reference

### [SERIE] Section

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `projects` | Yes | - | Comma-separated Git repository URLs |
| `commands` | Yes | - | Path to patch script |
| `commit_msg` | Yes | - | Commit message template |
| `topic` | No | "" | Gerrit topic name |
| `commit` | No | true | Auto-commit changes |
| `review` | No | false | Submit to Gerrit |
| `branch` | No | None | Target branch to switch to |
| `create_branch` | No | false | Create branch if it doesn't exist |
| `stay_on_branch` | No | false | Don't return to original branch |
| `pre_commands` | No | [] | Commands to run before changes (one per line) |
| `post_commands` | No | [] | Commands to run after changes (one per line) |
| `continue_on_error` | No | false | Continue if commands fail |
| `dry_run` | No | false | Preview without executing |

### [TESTS] Section

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `run` | No | false | Enable test execution |
| `blocking` | No | false | Fail on test failure |
| `command` | No | tox | Test command to run |

## Template Variables

The following variables can be used in `commit_msg`:

- `{{ project_name }}` - Name of the repository (extracted from URL)
- `{{project_name}}` - Alternative syntax without spaces

Example:
```ini
commit_msg = Update {{ project_name }} dependencies

             Bumps library-x to version 2.0 in {{ project_name }}.
```

**Automatic Sign-off**: All commits are automatically signed off using the `-s` flag. The tool will append a "Signed-off-by: Your Name <your.email@example.com>" line to your commit message using your Git configuration (`user.name` and `user.email`).

## Patch Script Guidelines

### Best Practices

1. **Exit codes**: Exit with 0 on success, non-zero on failure
2. **Idempotency**: Script should be safe to run multiple times
3. **Change detection**: Only make changes when necessary
4. **Error handling**: Use `set -e` to fail on errors
5. **Logging**: Print helpful messages for debugging

### Example Script

```bash
#!/bin/bash
set -e  # Exit on error

# Check if target file exists
if [ ! -f "requirements.txt" ]; then
    echo "No requirements.txt found"
    exit 0  # Not an error, just skip
fi

# Make the change
sed -i 's/library==1.0/library==2.0/' requirements.txt

# Verify the change
if grep -q "library==2.0" requirements.txt; then
    echo "Successfully updated library version"
else
    echo "Failed to update library version"
    exit 1
fi
```

## Testing Integration

### Running Tests

Enable testing in your configuration:

```ini
[TESTS]
run = true
blocking = true
command = pytest tests/
```

### Test Commands

Common test commands:
- `tox` - Run tox environments
- `pytest` - Run pytest
- `npm test` - Node.js tests
- `make test` - Makefile-based tests
- `./run_tests.sh` - Custom test script

### Blocking vs Non-Blocking

**Blocking** (`blocking = true`):
- Tests must pass for commit to be created
- Repository is marked as failed if tests fail
- Use for critical changes

**Non-Blocking** (`blocking = false`):
- Tests run but failures are warnings
- Commit is created even if tests fail
- Use for experimental changes

## Gerrit Integration

### Setup

1. Install git-review:
```bash
pip install git-review
```

2. Configure your repositories with `.gitreview` file

3. Enable review submission:
```ini
[SERIE]
review = true
topic = my-patch-series
```

### Workflow

1. Tool clones each repository
2. Automatically runs `git review -s` to setup Gerrit remote
3. Applies patches and creates commits locally (with automatic sign-off)
4. Submits to Gerrit with specified topic
5. All patches grouped under same topic
6. Review and merge through Gerrit UI

**Notes**:
- The tool automatically sets up git-review for each repository by running `git review -s` after cloning. This ensures the Gerrit remote is properly configured before submitting patches.
- All commits are automatically signed off using `git commit -s`, which adds a "Signed-off-by" line with your Git user name and email to the commit message.

## Error Handling

### Exit on Error

Use `--exit-on-error` to stop on first failure:

```bash
roller create --config-file series.ini --exit-on-error
```

### Continue on Error

Default behavior continues processing all repositories even if some fail.

### Debugging

1. Check the workspace directory (shown in output)
2. Inspect failed repositories manually
3. Use `--verbose` for detailed output
4. Review patch script logic

## Branch Switching

### Using the --branch Option

Apply changes to a specific branch:

```bash
roller create --config-file series.ini --branch stable/1.x
```

Create a new branch if it doesn't exist:

```bash
roller create --config-file series.ini --branch feature/new --create-branch
```

Stay on the target branch after completion:

```bash
roller create --config-file series.ini --branch dev --stay-on-branch
```

### Multi-Branch Backport

Apply the same fix to multiple branches:

```bash
for branch in main stable/2.x stable/1.x; do
  roller create --config-file security-fix.ini --branch $branch
done
```

## Command Execution

### Pre-Commands

Run commands before applying changes:

```bash
roller create --config-file series.ini \
  --pre-command "git pull origin main" \
  --pre-command "pytest tests/"
```

### Post-Commands

Run commands after applying changes:

```bash
roller create --config-file series.ini \
  --post-command "git add -A" \
  --post-command "git commit -m 'Auto-commit'" \
  --post-command "git push"
```

### Continue on Error

Continue processing even if commands fail:

```bash
roller create --config-file series.ini \
  --pre-command "npm test" \
  --continue-on-error
```

### Dry Run

Preview what would be executed without making changes:

```bash
roller create --config-file series.ini --dry-run
```

### Commands in Configuration File

You can also specify commands in the config file:

```ini
[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test

# Commands to run before applying changes
pre_commands = git checkout main
               git pull
               pytest tests/

# Commands to run after applying changes
post_commands = git add -A
                git commit -m "Auto-update"
                git push
```

**Security Warning**: Commands from configuration files pose a security risk. Only use configuration files from trusted sources, as they can execute arbitrary commands on your system.

## Examples

### Security Update

```ini
[SERIE]
projects = https://github.com/org/service1,
           https://github.com/org/service2,
           https://github.com/org/service3

commands = ./update_dependency.sh

commit_msg = Security update for {{ project_name }}

             Update vulnerable-lib to address CVE-2025-1234.

topic = security-cve-2025-1234
commit = true
review = true

[TESTS]
run = true
blocking = true
command = tox -e py39
```

### License Header Addition

```bash
#!/bin/bash
# add_license.sh

for file in $(find . -name "*.py" -type f); do
    if ! grep -q "SPDX-License-Identifier" "$file"; then
        # Add header
        cat license_header.txt "$file" > "$file.tmp"
        mv "$file.tmp" "$file"
    fi
done
```

```ini
[SERIE]
projects = https://github.com/org/lib1,
           https://github.com/org/lib2

commands = ./add_license.sh
commit_msg = Add SPDX license headers to {{ project_name }}
topic = license-compliance
commit = true
review = false
```

## Troubleshooting

### Common Issues

**Script not executable**
```bash
chmod +x your_script.sh
```

**Git authentication fails**
- Use SSH URLs with configured keys
- Or use HTTPS with credential helper

**No changes detected**
- Verify your script makes actual file changes
- Check script runs without errors

**Tests timeout**
- Increase timeout in repository.py
- Or disable blocking tests

## Advanced Usage

### Parallel Processing

The tool automatically processes repositories in parallel (up to 4 concurrent workers).

### Workspace Management

Workspaces are created in `/tmp/changes-roller-XXXXXX` by default. The workspace path is displayed at the start of execution.

To inspect a workspace after execution:
```bash
cd /tmp/changes-roller-abc123/repo-name
git log
git diff
```

### Custom Git Operations

Your patch script can use Git commands:

```bash
#!/bin/bash
# Create a new file
echo "content" > newfile.txt
git add newfile.txt

# Modify existing file
git mv oldname.txt newname.txt
```

## Tips and Best Practices

1. **Test locally first**: Run your patch script manually on one repo before running on all repos
2. **Use dry runs**: Set `commit = false` and `review = false` to test without committing
3. **Incremental rollout**: Start with a small subset of repos
4. **Version control configs**: Keep configuration files in Git
5. **Descriptive topics**: Use descriptive Gerrit topics for easier tracking
6. **Monitor progress**: Watch the output for any warnings or errors
7. **Review workspaces**: Check the workspace if something seems wrong

## Getting Help

```bash
roller --help
roller create --help
```

For issues and feature requests, visit the project repository.
