# PyPI Trusted Publisher Setup

This document provides instructions for configuring PyPI Trusted Publishers (OIDC-based publishing) for the changes-roller project.

## Overview

**Trusted Publishers** is PyPI's recommended secure method for automated package publishing. It uses OpenID Connect (OIDC) to authenticate GitHub Actions workflows without requiring API tokens.

## Benefits

- ✅ No API tokens to store or manage
- ✅ No secrets in GitHub repository
- ✅ Automatic token rotation
- ✅ Scoped permissions (specific repo + workflow only)
- ✅ Complete audit trail on PyPI

## Prerequisites

Before setting up trusted publishing:

1. The package must be registered on PyPI (upload at least one version manually first)
2. You must be a maintainer/owner of the package on PyPI
3. You must have access to the GitHub repository

## Step 1: Initial Package Registration

If this is the first time publishing the package, you must upload it manually first:

```bash
# Build the package
pip install --upgrade build hatchling
python -m build

# Upload to PyPI (you'll need your PyPI credentials)
pip install --upgrade twine
twine upload dist/*
```

After this initial upload, you won't need to use tokens anymore.

## Step 2: Configure Trusted Publisher on PyPI

### 2.1 Access PyPI Project Settings

1. Go to https://pypi.org/manage/project/changes-roller/settings/
2. Log in with your PyPI account (must have maintainer access)
3. Scroll to the **Publishing** section

### 2.2 Add Pending Publisher

Click **"Add a new pending publisher"** and fill in:

| Field                 | Value            |
| --------------------- | ---------------- |
| **PyPI Project Name** | `changes-roller` |
| **Owner**             | `k-pavlo`        |
| **Repository name**   | `changes-roller` |
| **Workflow filename** | `release.yml`    |
| **Environment name**  | `release`        |

### 2.3 Save Configuration

Click **"Add"** to save the trusted publisher configuration.

The publisher will show as "pending" until the first successful publish from GitHub Actions.

## Step 3: Configure GitHub Environment (Optional but Recommended)

Add extra protection by configuring the `release` environment in GitHub:

1. Go to https://github.com/k-pavlo/changes-roller/settings/environments
2. Click **"New environment"**
3. Name it: `release`
4. Configure protection rules:
   - ✅ **Required reviewers**: Add maintainers (optional)
   - ✅ **Deployment branches**: Select "Selected branches" → Add `main`
5. Click **"Save protection rules"**

This ensures releases can only be triggered from the `main` branch and optionally require manual approval.

## Step 4: Test the Setup

Create a test release to verify the configuration:

```bash
# 1. Ensure you're on main branch
git checkout main
git pull origin main

# 2. Bump version (or create a test tag manually)
cz bump

# 3. Push the tag
git push origin --tags

# 4. Monitor GitHub Actions
# Go to: https://github.com/k-pavlo/changes-roller/actions
# Watch the "Release to PyPI" workflow
```

### Expected Workflow Steps

1. ✅ **Build** - Package is built with hatchling
2. ✅ **Publish to PyPI** - Authenticates via OIDC and uploads
3. ✅ **Create GitHub Release** - Release is created with notes

### Verification

After workflow completes:

- **PyPI**: Visit https://pypi.org/project/changes-roller/ and verify new version is listed
- **GitHub**: Visit https://github.com/k-pavlo/changes-roller/releases and verify release is created
- **Install**: Test `pip install changes-roller==<version>`

## Troubleshooting

### "Trusted publisher validation failed"

**Problem**: PyPI cannot verify the OIDC token from GitHub Actions.

**Solutions**:

1. **Check PyPI configuration**:
   - Verify owner name matches: `k-pavlo`
   - Verify repo name matches: `changes-roller`
   - Verify workflow name matches: `release.yml`
   - Verify environment name matches: `release`

2. **Check GitHub workflow**:
   - Verify workflow file is named `.github/workflows/release.yml`
   - Verify workflow uses `environment: release`
   - Verify workflow has `permissions: id-token: write`

3. **Check workflow trigger**:
   - Trusted publishing only works when triggered by tag push matching the pattern
   - Manual workflow runs won't work if they don't set the environment correctly

### "This filename has already been used"

**Problem**: Trying to re-upload the same version to PyPI.

**Solution**: PyPI doesn't allow re-uploading the same version. Bump to a new version.

### "Publisher is pending"

**Problem**: Trusted publisher shows as "pending" on PyPI.

**Solution**: This is normal before the first successful publish. After the first successful automated publish from GitHub Actions, it will change to "active".

### "403 Forbidden" when publishing

**Problem**: Workflow doesn't have permission to publish.

**Solutions**:

1. Verify the PyPI project name matches exactly: `changes-roller`
2. Ensure the workflow is running from the correct repository
3. Check that the workflow has the correct environment configured
4. Verify `id-token: write` permission is set

## Additional Resources

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPA Publishing Action](https://github.com/pypa/gh-action-pypi-publish)

## Support

If you encounter issues:

1. Check the workflow logs in GitHub Actions
2. Review the PyPI trusted publisher configuration
3. Consult the resources above
4. Open an issue on the repository for help

## Migration from Token-based Publishing

If you previously used API tokens:

1. Remove the `PYPI_API_TOKEN` secret from GitHub repository settings
2. Configure trusted publisher as described above
3. The workflow already supports trusted publishing (no changes needed)
4. Previous token-based uploads are still valid and don't need to be redone

## Security Notes

- **No secrets required**: Trusted publishing uses OIDC, not static tokens
- **Automatic rotation**: Authentication tokens are ephemeral (valid only for the workflow run)
- **Audit trail**: All publishes are logged on PyPI with full context
- **Scoped access**: Publisher can only publish to the specific package from the specific repo/workflow
- **Revocable**: Publisher can be removed from PyPI settings at any time

## Maintenance

The trusted publisher configuration should not need regular maintenance. However:

- If you rename the repository, update the trusted publisher configuration
- If you rename the workflow file, update the trusted publisher configuration
- If you change the environment name, update both PyPI and the workflow
- Review active publishers periodically in PyPI settings
