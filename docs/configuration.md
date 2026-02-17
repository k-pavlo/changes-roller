# Configuration Reference

This page provides a complete reference for all configuration options in changes-roller.

## Configuration File Format

changes-roller uses INI format configuration files with two main sections:

- `[SERIE]` - Patch series configuration
- `[TESTS]` - Test execution configuration (optional)

## [SERIE] Section

### Required Options

#### projects

**Type:** Comma-separated list of URLs
**Required:** Yes

List of Git repository URLs to patch. Each repository will be cloned and processed.

```ini
projects = https://github.com/org/repo1,
           https://github.com/org/repo2,
           https://github.com/org/repo3
```

You can also use SSH URLs:

```ini
projects = git@github.com:org/repo1.git,
           git@github.com:org/repo2.git
```

#### commands

**Type:** File path
**Required:** Yes

Path to the executable script that performs the patch operations. The script is executed in the context of each cloned repository.

```ini
commands = ./my-patch.sh
```

The script:

- Must be executable (`chmod +x script.sh`)
- Runs with the repository directory as the working directory
- Should exit with code 0 on success, non-zero on failure
- Can make any file system changes

#### commit_msg

**Type:** Multi-line string
**Required:** Yes

Commit message template. Supports variable substitution with `{{ project_name }}`.

```ini
commit_msg = Update dependencies in {{ project_name }}

             This patch updates the library to version 2.0 for
             improved security and performance.

             Closes-Bug: #12345
```

Variables:

- `{{ project_name }}` - Name of the repository being processed

### Optional Options

#### topic

**Type:** String
**Default:** None

Topic name for grouping related patches in Gerrit code review.

```ini
topic = dependency-update-2025
```

#### commit

**Type:** Boolean
**Default:** true

Whether to create Git commits automatically.

```ini
commit = true
```

Set to `false` to only apply changes without committing (useful for manual review).

#### review

**Type:** Boolean
**Default:** false

Whether to submit patches to Gerrit for code review using `git review`.

```ini
review = true
```

Requires:

- `git-review` installed
- Repository configured for Gerrit
- Proper authentication set up

#### branch

**Type:** String
**Default:** None

Target branch to switch to before applying changes.

```ini
branch = stable/2024.2
```

This is useful for:

- Applying backport fixes to stable branches
- Multi-branch maintenance
- Testing changes on specific branches

#### create_branch

**Type:** Boolean
**Default:** false

Create the target branch if it doesn't exist. Requires `branch` option.

```ini
branch = feature/new-api
create_branch = true
```

#### stay_on_branch

**Type:** Boolean
**Default:** false

Don't return to the original branch after processing. By default, changes-roller returns to the original branch after completion.

```ini
branch = stable/2024.2
stay_on_branch = true
```

#### pre_commands

**Type:** Multi-line string (one command per line)
**Default:** None

Commands to execute before applying changes. Useful for setup operations.

```ini
pre_commands = git pull origin main
               npm install
               make clean
```

#### post_commands

**Type:** Multi-line string (one command per line)
**Default:** None

Commands to execute after committing changes. Useful for cleanup or deployment.

```ini
post_commands = git push origin main
                notify-team.sh
```

#### continue_on_error

**Type:** Boolean
**Default:** false

Continue processing if pre/post commands fail, instead of stopping.

```ini
continue_on_error = true
```

#### dry_run

**Type:** Boolean
**Default:** false

Preview operations without executing them. Shows what would happen without making changes.

```ini
dry_run = true
```

## [TESTS] Section

Optional section for configuring test execution before committing.

### run

**Type:** Boolean
**Default:** false

Whether to run tests before creating commits.

```ini
[TESTS]
run = true
```

### blocking

**Type:** Boolean
**Default:** false

Whether to fail the patch if tests fail. If `false`, test failures are logged but don't prevent commits.

```ini
[TESTS]
run = true
blocking = true
```

### command

**Type:** String
**Default:** tox

Command to execute for testing.

```ini
[TESTS]
run = true
command = pytest tests/
```

Common examples:

- `tox` - Run tox test environments
- `tox -e pep8` - Run only PEP8 checks
- `pytest tests/` - Run pytest tests
- `npm test` - Run npm tests
- `make test` - Run makefile tests

## Complete Example

```ini
[SERIE]
# Repositories to patch
projects = https://github.com/org/service-a,
           https://github.com/org/service-b,
           https://github.com/org/service-c

# Patch script
commands = ./security-patch.sh

# Commit message with variable
commit_msg = Security fix for CVE-2025-1234 in {{ project_name }}

             This patch addresses a critical security vulnerability
             in the authentication module.

             Security-Bug: CVE-2025-1234

# Code review settings
topic = security-cve-2025-1234
review = true

# Branch settings (apply to stable branch)
branch = stable/2024.2
create_branch = false
stay_on_branch = false

# Execute commands
pre_commands = git pull origin stable/2024.2
               git clean -fdx

post_commands = git push origin stable/2024.2

# Error handling
continue_on_error = false

# Commit changes
commit = true

[TESTS]
# Run security tests before committing
run = true
blocking = true
command = bandit -r . && pytest tests/security/
```

## Command-Line Overrides

Most configuration options can be overridden via command-line flags:

```bash
roller create --config-file series.ini \
  --branch stable/2024.1 \
  --create-branch \
  --dry-run \
  --pre-command "git pull" \
  --post-command "git push" \
  --exit-on-error
```

Command-line options take precedence over configuration file settings.

## Best Practices

1. **Use dry-run first** - Always test with `--dry-run` before executing
2. **Version control your configs** - Keep configuration files in Git
3. **Descriptive commit messages** - Include context and references (bug IDs, tickets)
4. **Test in isolation** - Test your patch script on a single repo first
5. **Use topics** - Group related patches with meaningful topic names
6. **Enable blocking tests** - Prevent commits if critical tests fail
7. **Document your scripts** - Add comments to patch scripts explaining the changes
