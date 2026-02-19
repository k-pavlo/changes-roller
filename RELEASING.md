# Release Process

This document is for project maintainers. Contributors do not need to perform these steps.

## Overview

This project uses automated versioning and releasing:

1. **Conventional commits** drive semantic versioning
2. **Commitizen** calculates versions and updates files
3. **GitHub Actions** builds and publishes to PyPI automatically
4. **Release Drafter** generates release notes from commits

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.0.0): Incompatible API changes
- **MINOR** version (0.1.0): New functionality (backwards compatible)
- **PATCH** version (0.0.1): Bug fixes (backwards compatible)

### How Version Bumping Works

Versions are automatically calculated from conventional commit messages:

- `feat:` commits → MINOR version bump (0.1.0 → 0.2.0)
- `fix:` commits → PATCH version bump (0.1.0 → 0.1.1)
- `BREAKING CHANGE:` in commit footer → MAJOR version bump (0.1.0 → 1.0.0)
- Other commit types (docs, style, chore) → No version bump

## Creating a Release

### Step 1: Ensure Main Branch is Ready

```bash
# Switch to main and pull latest
git checkout main
git pull origin main

# Verify everything is clean
git status

# Run all quality checks
pre-commit run --all-files
pytest
```

### Step 2: Bump Version with Commitizen

```bash
# Preview the version bump
cz bump --dry-run

# Bump the version
cz bump

# This automatically:
# - Analyzes commits since last version
# - Calculates version increment (feat→MINOR, fix→PATCH, BREAKING→MAJOR)
# - Updates pyproject.toml and roller/__init__.py
# - Updates CHANGELOG.md with release notes
# - Creates a git commit with changes
# - Creates a version tag (e.g., v0.2.0)

# Review the changes
git log -1 --stat
git show HEAD
```

### Step 3: Create Merge Request (Do NOT Push Tag Yet)

Since the main branch is protected and requires merge requests:

```bash
# Create a release branch
git checkout -b release/v$(git describe --tags --abbrev=0 | sed 's/v//')

# Push ONLY the branch (NOT the tag yet)
git push origin release/v$(git describe --tags --abbrev=0 | sed 's/v//')

# Create merge request from your release branch to main
# (Use your Git hosting platform's UI or CLI)
```

**IMPORTANT:** Do NOT push the tag yet. Environment protection rules prevent releases from non-main branches.

### Step 4: Push Tag After PR Merge

After your PR is approved and merged to main:

```bash
# Switch to main and pull the merged changes
git checkout main
git pull origin main

# Now push the tag to trigger the release
git push origin --tags
```

**How it works:**

- The release workflow triggers when a tag matching `v*` is pushed to GitHub
- Environment protection rules require the tag to point to a commit on main
- Pushing the tag before the PR merge will cause the workflow to fail
- Once the PR is merged and you push the tag, the pipeline runs successfully

### Step 5: Monitor Release Workflow

1. Go to **Actions** tab on GitHub
2. Watch the **Release to PyPI** workflow
3. Verify all jobs succeed:
   - ✅ Build distribution packages
   - ✅ Publish to PyPI
   - ✅ Create GitHub Release

### Step 6: Verify Release

**Check PyPI:**

- Visit: https://pypi.org/project/changes-roller/
- Verify new version is published
- Test installation: `pip install changes-roller==<version>`

**Check GitHub Release:**

- Visit: https://github.com/k-pavlo/changes-roller/releases
- Verify release is created with proper notes
- Check that distribution files are attached

## Manual Version Override

Force a specific version increment if needed:

```bash
cz bump --increment MAJOR   # Force major version bump
cz bump --increment MINOR   # Force minor version bump
cz bump --increment PATCH   # Force patch version bump
```

## Hotfix Releases

For urgent bug fixes that need immediate release:

```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/critical-fix main

# 2. Make minimal fixes
# ... edit code ...

# 3. Commit with conventional commit message
git commit -m "fix: resolve critical security vulnerability"

# 4. Bump version (will be PATCH increment)
cz bump

# 5. Push branch only (NOT the tag)
git push origin hotfix/critical-fix

# 6. Create merge request to main and get it merged

# 7. After PR is merged, push the tag to trigger release
git checkout main
git pull origin main
git push origin --tags
```

## Pre-release Versions

For testing before official release:

```bash
# Manually edit version in pyproject.toml and roller/__init__.py
# Example: version = "0.2.0rc1"  # Release candidate

# Commit and tag
git commit -m "chore: prepare release candidate 0.2.0rc1"
git tag v0.2.0rc1
git push origin main --tags

# This publishes to PyPI as pre-release
# Users can install with: pip install --pre changes-roller
```

## Rollback Strategies

If a release has issues:

### Option 1: Yank Release (PyPI)

Prevents new installations but doesn't break existing ones:

1. Go to https://pypi.org/manage/project/changes-roller/releases/
2. Find the problematic version
3. Click "Options" → "Yank release"
4. Provide reason for yanking

### Option 2: Release Fix Immediately

```bash
# 1. Create fix branch
git checkout -b fix/regression main

# 2. Fix the issue
git commit -m "fix: resolve regression in v0.2.0"

# 3. Bump version (PATCH increment)
cz bump

# 4. Push branch only (NOT the tag)
git push origin fix/regression

# 5. Create merge request and get it merged

# 6. After PR is merged, push the tag to trigger release
git checkout main
git pull origin main
git push origin --tags
```

## Changelog Management

### Format

We follow [Keep a Changelog v1.0.0](https://keepachangelog.com/en/1.0.0/) format.

### Categories

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes

### Automated Updates

When you run `cz bump`, CHANGELOG.md is automatically updated with:

- All commits since last version
- Organized by type (feat → Added, fix → Fixed)
- Version number and date
- Links to GitHub compare view

## Automated Release Pipeline

### Trusted Publishers (OIDC)

This project uses **Trusted Publishers** for secure PyPI authentication:

**What it is:**

- Token-free authentication using OpenID Connect (OIDC)
- GitHub Actions authenticates directly with PyPI
- No long-lived API tokens to manage or secure
- Scoped to specific repository and workflow

**Security benefits:**

- ✅ No secrets stored in GitHub repository
- ✅ Automatic token rotation via OIDC
- ✅ Scoped permissions to specific repo/workflow
- ✅ Audit trail of all publishing events
- ✅ Cannot be leaked - tokens are ephemeral

**Configuration:**

On PyPI (already configured):

- Go to: https://pypi.org/manage/project/changes-roller/settings/
- Navigate to "Publishing" tab
- Trusted publisher configured with:
  - Owner: `k-pavlo`
  - Repository: `changes-roller`
  - Workflow: `release.yml`
  - Environment: `release`

### Release Workflow Details

The `.github/workflows/release.yml` workflow includes three jobs:

**1. Build (runs on all platforms)**

- Checks out code
- Sets up Python 3.12
- Builds wheel and source distribution with hatchling
- Uploads artifacts for publishing

**2. Publish to PyPI (runs after build)**

- Downloads built distributions
- Authenticates via OIDC (no token needed)
- Publishes to PyPI using `pypa/gh-action-pypi-publish`
- Uses `release` environment for protection

**3. Create GitHub Release (runs after publish)**

- Creates GitHub Release from tag
- Auto-generates release notes from commits
- Attaches distribution files
- Links to PyPI package page

## Release Drafter

This project uses **GitHub Release Drafter** to automatically generate and maintain draft release notes.

### How It Works

Release Drafter automatically:

- **Monitors merged PRs** - Runs on every push to main
- **Updates draft release** - Continuously maintains next release draft
- **Categorizes changes** - Groups PRs by type (Features, Bug Fixes, etc.)
- **Auto-labels PRs** - Labels PRs based on conventional commit prefixes in titles
- **Suggests version** - Calculates next version based on PR labels

### Release Note Categories

PRs are automatically categorized:

| Category         | Labels/Prefixes                 | Examples                 |
| ---------------- | ------------------------------- | ------------------------ |
| 🚀 Features      | `feat:`, `feature`              | New functionality        |
| 🐛 Bug Fixes     | `fix:`, `bug`                   | Bug fixes                |
| 📚 Documentation | `docs:`, `documentation`        | Docs updates             |
| 🔧 Maintenance   | `chore:`, `ci:`, `dependencies` | Maintenance tasks        |
| ⚡ Performance   | `perf:`, `performance`          | Performance improvements |
| 🔒 Security      | `security`                      | Security fixes           |

### Auto-labeling

PRs are automatically labeled based on their title:

```
feat: Add branch switching support → labeled "feature"
fix: Resolve path issue → labeled "bug"
docs: Update README → labeled "documentation"
chore: Update dependencies → labeled "chore"
```

### Viewing Draft Releases

To see the current draft release:

1. Navigate to https://github.com/k-pavlo/changes-roller/releases
2. Look for the release marked as **"Draft"**
3. This shows what the next release notes will look like

Draft releases are:

- Created automatically after first PR merge
- Updated automatically on every merge to main
- Not visible to the public (only maintainers)
- Ready to publish when you're ready to release

### Publishing a Release

The release workflow automatically creates and publishes the GitHub Release when you push a version tag.

```bash
# After running cz bump, push ONLY the branch
git push origin your-release-branch

# Create and merge MR to main

# After PR is merged, pull main and push the tag
git checkout main
git pull origin main
git push origin --tags  # This triggers automatic release creation
```

**Important:** The tag must point to a commit on main to satisfy environment protection rules.

The automatic release includes:

- Release notes from commits (via `generate_release_notes: true`)
- Installation instructions
- Link to CHANGELOG.md
- Link to PyPI package
- Distribution files attached

## Troubleshooting

### "No commits found to bump version"

**Cause:** No commits with feat/fix/BREAKING CHANGE since last version

**Solution:** This is expected; version only bumps when there's new functionality or fixes

### "Version file not found"

**Cause:** Version format doesn't match expected pattern

**Solution:** Ensure version format matches: `version = "X.Y.Z"` and `__version__ = "X.Y.Z"`

### "Trusted publisher validation failed"

**Cause:** OIDC configuration mismatch between PyPI and GitHub workflow

**Solution:**

1. Verify PyPI trusted publisher settings match workflow
2. Ensure workflow uses `release` environment
3. Check that workflow has `id-token: write` permission

### "Package already exists on PyPI"

**Cause:** Trying to re-upload same version

**Solution:**

1. PyPI doesn't allow re-uploading same version
2. Bump to new version and release again
3. If needed, yank the old version on PyPI

### "Build failed"

**Cause:** Package build error with hatchling

**Solution:**

```bash
# Test build locally
pip install --upgrade build hatchling
python -m build

# Fix any build errors and commit
```

### "GitHub Release creation failed"

**Cause:** Workflow lacks permissions or tag already has release

**Solution:**

1. Check workflow has `contents: write` permission
2. Delete existing release if re-creating
3. Re-run workflow from Actions tab

## Release Checklist

Before creating a release:

- [ ] All tests passing in CI
- [ ] All PRs merged that should be in release
- [ ] CHANGELOG.md reviewed (will be auto-updated by `cz bump`)
- [ ] Version calculated correctly with `cz bump --dry-run`
- [ ] Tag created and pushed
- [ ] GitHub Actions workflow succeeded
- [ ] PyPI package published and installable
- [ ] GitHub Release created automatically
- [ ] Documentation updated on ReadTheDocs
- [ ] Release notes reviewed
- [ ] Announcement drafted (if major release)

## Support Policy

**Python versions:** Currently supporting Python 3.10+

**Platform support:** Linux, macOS, Windows

**Dependencies:** Automated updates via Dependabot, reviewed before merge

**Breaking changes:**

- CLI flag deprecation: Warn first, remove in next major version
- Version signaling: Use semantic versioning (MAJOR for breaking changes)
- Migration guide: Provide in CHANGELOG.md and documentation for breaking changes
