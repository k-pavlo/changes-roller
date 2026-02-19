# Oslo Dependency Update Example

This example demonstrates how to update a dependency across multiple OpenStack oslo libraries using changes-roller with Gerrit integration.

## Scenario

Update the `pbr` (Python Build Reasonableness) library to version 6.0.0 across all oslo.\* repositories in the OpenStack project.

## Background

OpenStack's oslo libraries provide shared functionality used across many OpenStack projects. When a core dependency like pbr needs updating, it must be updated consistently across all oslo repositories. This example shows how changes-roller automates this process.

## Files

- `patch.sh`: Shell script that updates the pbr version in requirements files
- `series.ini`: Configuration file defining the patch series

## Prerequisites

- Git command-line client
- Python 3.10+ with tox installed
- git-review (optional, for Gerrit submission)

## Usage

```bash
# From the repository root, run with dry-run first
roller create --config-file examples/oslo-dependency-update/series.ini --dry-run

# Review the dry-run output, then execute for real
roller create --config-file examples/oslo-dependency-update/series.ini
```

## What Happens

1. **Clones repositories**: Downloads each oslo.\* repository listed in series.ini
2. **Runs patch script**: Executes `patch.sh` to update pbr version in:
   - requirements.txt
   - pyproject.toml
   - test-requirements.txt
3. **Runs tests**: Executes `tox -e py310` to verify compatibility (non-blocking)
4. **Creates commits**: Generates commits with templated messages including project name
5. **Groups with topic**: All patches share the `oslo-pbr-update` Gerrit topic
6. **(Optional) Submits to Gerrit**: If `review = true`, submits patches for code review

## Customization

### Update Different Dependency

Edit `patch.sh` to change the dependency being updated:

```bash
# Instead of pbr
sed -i 's/requests>=.*$/requests>=2.28.0/' requirements.txt
```

### Change Oslo Projects

Edit `series.ini` to add or remove oslo libraries:

```ini
projects = https://github.com/openstack/oslo.config,
           https://github.com/openstack/oslo.middleware,
           https://github.com/openstack/oslo.serialization
```

### Adjust Test Command

Modify the test command in `series.ini`:

```ini
[TESTS]
command = tox -e pep8,py311
```

### Enable Gerrit Submission

To submit patches to Gerrit for review, set:

```ini
review = true
```

Note: Requires `git-review` to be installed and configured.

## Branch Variations

To apply this patch to a stable branch instead of main:

```bash
roller create --config-file examples/oslo-dependency-update/series.ini --branch stable/2024.1
```

To apply across multiple stable branches:

```bash
for branch in stable/2024.1 stable/2024.2 stable/2025.1; do
    roller create --config-file examples/oslo-dependency-update/series.ini --branch $branch
done
```

## Expected Output

```
Processing 6 repositories...
✓ oslo.config: Patch applied successfully
✓ oslo.messaging: Patch applied successfully
✓ oslo.db: Patch applied successfully
✓ oslo.log: Patch applied successfully
✓ oslo.policy: Patch applied successfully
✓ oslo.utils: Patch applied successfully

Summary: 6 successful, 0 failed
```

## Notes

- **Non-blocking tests**: Tests run but don't fail the patch if they fail (blocking = false)
- **Gerrit topic**: All patches are grouped under `oslo-pbr-update` topic for easier review
- **Parallel execution**: All repositories are processed concurrently for speed
- **Real repositories**: This example uses actual OpenStack repositories (requires network access)

## Further Reading

- [Oslo Project Documentation](https://docs.openstack.org/oslo/)
- [pbr Documentation](https://docs.openstack.org/pbr/latest/)
- [OpenStack Gerrit Workflow](https://docs.openstack.org/contributors/common/setup-gerrit.html)
