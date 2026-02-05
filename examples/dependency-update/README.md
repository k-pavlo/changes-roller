# Dependency Update Example

This example demonstrates how to update a Python dependency across multiple repositories.

## Scenario

Update the `hacking` library from version 3.x to 4.x across all OpenStack projects.

## Files

- `patch.sh`: Shell script that performs the actual update
- `series.ini`: Configuration file defining the patch series

## Usage

```bash
# From the repository root
roller create --config-file examples/dependency-update/series.ini
```

## What Happens

1. Clones each repository
2. Runs the patch script to update requirements.txt
3. Runs tests (tox) to ensure compatibility
4. Commits changes with the templated message
5. (Optional) Submits to Gerrit for review

## Customization

- Edit `series.ini` to change the list of projects
- Modify `patch.sh` to update different dependencies
- Adjust test command in the [TESTS] section
