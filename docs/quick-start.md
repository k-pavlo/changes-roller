# Quick Start

Get started with changes-roller in 5 minutes.

## Step 1: Generate a Configuration File

```bash
roller init --output my-series.ini
```

This creates a template configuration file with all available options documented.

## Step 2: Create a Patch Script

Create an executable script that performs your desired changes:

```bash
#!/bin/bash
# Example: Update a dependency version
sed -i 's/old-library==1.0/old-library==2.0/' requirements.txt
```

Save this as `my_patch.sh` and make it executable:

```bash
chmod +x my_patch.sh
```

## Step 3: Edit the Configuration File

Open `my-series.ini` and configure your patch series:

```ini
[SERIE]
# List your repositories (comma-separated)
projects = https://github.com/org/repo1,
           https://github.com/org/repo2,
           https://github.com/org/repo3

# Point to your patch script
commands = ./my_patch.sh

# Set your commit message
commit_msg = Update old-library to version 2.0

             This update includes important security fixes
             and performance improvements.

# Optional: Group patches under a topic for code review
topic = library-update-2025

# Create commits automatically
commit = true

# Submit to Gerrit for review (set to true if using Gerrit)
review = false

[TESTS]
# Optionally run tests before committing
run = false
blocking = false
command = tox
```

## Step 4: Run the Patch Series

```bash
roller create --config-file my-series.ini
```

That's it! changes-roller will:

1. Clone each repository
2. Execute your patch script
3. Commit the changes
4. Optionally run tests
5. Optionally submit for code review

## What's Next?

- Read the [Usage Guide](usage.md) for detailed instructions
- Explore [Configuration](configuration.md) for all available options
- Check out [Examples](examples.md) for common use cases
- See the [API Reference](autoapi/index.html) for programmatic usage

## Common First Steps

### Preview Changes (Dry Run)

Test your configuration without making any changes:

```bash
roller create --config-file my-series.ini --dry-run
```

### Apply to a Specific Branch

Apply changes to a stable branch instead of the default:

```bash
roller create --config-file my-series.ini --branch stable/2024.2
```

### Run Commands Before/After

Execute commands before and after applying changes:

```bash
roller create --config-file my-series.ini \
  --pre-command "git pull origin main" \
  --post-command "git push origin main"
```

### Exit on First Failure

Stop immediately if any repository fails:

```bash
roller create --config-file my-series.ini --exit-on-error
```

## Getting Help

```bash
# General help
roller --help

# Help for specific command
roller create --help
roller init --help
```

For more examples and advanced usage, continue to the [Usage Guide](usage.md).
