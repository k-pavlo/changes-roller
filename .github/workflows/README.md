# GitHub Actions Workflows

This directory contains CI/CD workflows for the changes-roller project.

## Workflows

### ci.yml - Main CI Pipeline

**Triggers:** Push to main, Pull requests, Manual dispatch

**Purpose:** Comprehensive testing and quality checks

**Jobs:**

1. **lint-and-format** (~2 min)
   - Runs pre-commit hooks (Ruff format, Ruff lint, Prettier, file validation)
   - Uses pre-commit cache for faster execution
   - Blocks subsequent jobs if quality checks fail

2. **type-check** (~2 min)
   - MyPy strict type checking on Python 3.10 (strictest baseline)
   - Uses mypy cache for faster execution
   - Runs in parallel with lint-and-format

3. **test** (~5-10 min)
   - Matrix testing: Python 3.10-3.13 × Linux/macOS/Windows
   - Optimized to 8 jobs (all Python versions on Linux, only 3.10+3.13 on macOS/Windows)
   - Runs after lint-and-format and type-check pass
   - Coverage collected on ubuntu-latest + Python 3.12
   - Coverage uploaded to Codecov

4. **test-summary** (<1 min)
   - Aggregates test results from all matrix jobs
   - Single required status check for branch protection
   - Always runs even if tests fail

**Required for merge:** Yes (all jobs must pass)

**Optimizations:**

- Path ignore: Skips CI for docs-only changes (\*.md, docs/, examples/)
- Concurrency control: Cancels old runs when new commits pushed
- Multi-tier caching: pre-commit, pip, mypy

---

### security.yml - Security Scanning

**Triggers:** Pull requests, Weekly schedule (Monday 00:00 UTC), Manual dispatch

**Purpose:** Security vulnerability detection

**Jobs:**

1. **bandit** (~1-2 min)
   - Python code security scanning
   - Uses configuration from pyproject.toml
   - Required for merge

2. **pip-audit** (~1-2 min)
   - Dependency vulnerability scanning
   - Warning only (not blocking)
   - Helps identify outdated/vulnerable dependencies

3. **dependency-review** (~1 min)
   - GitHub's dependency review action
   - Only runs on PRs
   - Blocks PRs introducing dependencies with moderate+ severity vulnerabilities
   - Required for merge

**Required for merge:** Yes (bandit and dependency-review must pass)

---

### release.yml - PyPI Publishing

**Triggers:** Version tag push (`v*`), Manual dispatch

**Purpose:** Automated package publishing to PyPI and GitHub Releases

**Jobs:**

1. **build** (~2 min)
   - Builds wheel and source distribution with hatchling
   - Uploads distribution artifacts

2. **publish-to-pypi** (~1-2 min)
   - Downloads built distributions
   - Publishes to PyPI using trusted publisher (OIDC)
   - Uses `release` environment for protection
   - No API token needed (secure OIDC authentication)

3. **github-release** (~1 min)
   - Creates GitHub Release from tag
   - Auto-generates release notes from commits
   - Attaches distribution files
   - Links to PyPI package page

**Required for merge:** No (runs only on tag push)

**Security:** Uses OpenID Connect (OIDC) trusted publisher for secure, token-free PyPI authentication

---

### release-drafter.yml - Automated Release Notes

**Triggers:** Push to main, Pull requests

**Purpose:** Automatically generate and maintain draft release notes

**Jobs:**

1. **update_release_draft** (~30 sec)
   - Monitors merged PRs to main branch
   - Updates draft release with categorized changes
   - Auto-labels PRs based on conventional commit prefixes
   - Suggests next version based on PR labels

**Required for merge:** No (informational only)

**How it works:**

- Every PR merged to main updates the draft release
- PRs are categorized by type (Features, Bug Fixes, Docs, etc.)
- Uses conventional commit prefixes for auto-labeling:
  - `feat:` → Features 🚀
  - `fix:` → Bug Fixes 🐛
  - `docs:` → Documentation 📚
  - `chore:`, `ci:` → Maintenance 🔧
  - `perf:` → Performance ⚡
  - Security-related → Security 🔒

**View draft releases:** https://github.com/k-pavlo/changes-roller/releases (maintainers only)

**Configuration:** `.github/release-drafter.yml` defines categories, auto-labeling rules, and release note template

---

## Local Development

Run CI checks locally before pushing:

### Quick Pre-flight Check

```bash
# Run all pre-commit hooks (matches CI lint-and-format)
pre-commit run --all-files
```

### Full Local CI Simulation

```bash
# 1. Code quality (matches lint-and-format)
pre-commit run --all-files

# 2. Type checking (matches type-check)
mypy roller/

# 3. Tests (matches test job)
pytest --cov=roller --cov-report=term-missing

# 4. Security (matches security workflow)
bandit -c pyproject.toml -r roller/
pip-audit
```

### Run Specific Checks

```bash
# Just formatting
ruff format . --check
ruff check .

# Just tests
pytest

# Just type checking
mypy roller/

# Just security
bandit -c pyproject.toml -r roller/
```

---

## Caching Strategy

Workflows use multi-tier caching to speed up CI:

### Pre-commit Cache

- **Path:** `~/.cache/pre-commit`
- **Key:** Hash of `.pre-commit-config.yaml`
- **Hit rate:** ~95% (only changes when config updates)
- **Saves:** 30-60 seconds per run

### Pip Cache

- **Path:** Automatic (via `setup-python` with `cache: 'pip'`)
- **Key:** Hash of `pyproject.toml` and `requirements.txt`
- **Hit rate:** ~80% (changes with dependency updates)
- **Saves:** 20-40 seconds per run

### MyPy Cache

- **Path:** `.mypy_cache`
- **Key:** Hash of Python version + `roller/**/*.py`
- **Hit rate:** ~70% (changes with source code)
- **Saves:** 10-20 seconds per run

**View current caches:** Repository → Actions → Caches

---

## Required Secrets

### For CI Workflow

**CODECOV_TOKEN** (optional but recommended)

- Used to upload coverage reports to Codecov
- Get from: https://codecov.io after linking repository
- Add to: Repository Settings → Secrets and variables → Actions
- Without this: Coverage upload will work for public repos but may be rate-limited

### For Future Release Workflow

**PYPI_API_TOKEN** (not yet needed)

- Will be used for automated PyPI publishing
- Get from: https://pypi.org/manage/account/token/
- Add when implementing release workflow (Issue #5)

---

## Branch Protection Configuration

The `main` branch requires:

**Status checks:**

- `test-summary` (from ci.yml)
- `lint-and-format` (from ci.yml)
- `type-check` (from ci.yml)
- `bandit` (from security.yml)
- `dependency-review` (from security.yml)

**Pull request requirements:**

- 1 approval required
- Stale approvals dismissed on new commits
- Branches must be up to date before merging

**Other restrictions:**

- Linear history required (no merge commits)
- Force pushes disabled
- Branch deletion disabled
- Settings cannot be bypassed

**Why test-summary instead of individual test jobs?**

- Matrix changes (adding Python 3.14) won't break branch protection
- Single check is cleaner in PR UI
- Still enforces all tests pass (test-summary fails if any test job fails)

---

## Troubleshooting

### Workflow not triggering

**Check workflow syntax:**

```bash
# Install actionlint (optional)
brew install actionlint  # macOS
# or: sudo apt install actionlint  # Ubuntu
# or: winget install actionlint  # Windows

# Validate workflow files
actionlint .github/workflows/*.yml
```

**Verify branch name matches trigger pattern:**

- Workflows trigger on `main` branch and PRs
- Check that your branch/PR targets `main`

### Jobs timing out

**Default timeout:** 360 minutes (6 hours)
**Typical duration:** 2-10 minutes per workflow

If seeing consistent timeouts:

- Check for infinite loops in tests
- Verify dependencies install correctly
- Check Actions tab → Job logs for details

### Caches not working

**Cache invalidation:**

- Cache keys use file hashes
- Changes to config files invalidate cache
- This is expected behavior

**Check cache status:**

- Repository → Actions → Caches
- Shows all caches, last used, size

**Clear all caches:**

- Actions → Caches → Delete all caches
- Useful if cache corruption suspected

### Coverage upload failing

**Common causes:**

1. Missing CODECOV_TOKEN (optional for public repos)
2. Codecov API downtime (check status.codecov.io)
3. Invalid coverage.xml file

**Solution:**

- Coverage upload is non-blocking (`fail_ci_if_error: false`)
- Job will succeed even if upload fails
- Fix token if needed, re-run workflow

### Security scan false positives

**Bandit false positives:**

- Review findings in job logs
- Add `# nosec` comment with justification if safe
- Update `pyproject.toml` [tool.bandit] config if needed

**pip-audit false positives:**

- pip-audit is non-blocking (`continue-on-error: true`)
- Review vulnerabilities, update if necessary
- Can be ignored if not applicable

---

## Modifying Workflows

When modifying workflows:

### Best Practices

1. **Test locally first**
   - Use `act` (https://github.com/nektos/act) to test workflows locally (optional)
   - Run pre-commit and pytest before pushing

2. **Use workflow_dispatch for testing**
   - All workflows have manual trigger
   - Test workflow changes without creating PRs

3. **Update documentation**
   - Update this README if adding new workflows
   - Update CONTRIBUTING.md if changing contributor-facing behavior

4. **Update branch protection**
   - If adding new required jobs, update branch protection rules
   - Repository Settings → Branches → main → Edit

5. **Consider backward compatibility**
   - Old PRs still need to pass with new workflow
   - Avoid breaking changes to job names used in branch protection

### Adding a New Workflow

1. Create `.github/workflows/new-workflow.yml`
2. Add documentation to this README
3. Test with workflow_dispatch trigger
4. Update branch protection if check should be required
5. Announce change to contributors (if significant)

### Changing Matrix Strategy

**Current matrix:** 8 jobs

- Python 3.10, 3.11, 3.12, 3.13 on ubuntu-latest
- Python 3.10, 3.13 on macos-latest
- Python 3.10, 3.13 on windows-latest

**To add Python 3.14:**

- Add `'3.14'` to `python-version` array
- Will create 10 jobs (all on Linux, boundaries on macOS/Windows)

**To reduce CI minutes:**

- Add more OS/Python combinations to `exclude` list
- Remove older Python versions when EOL

---

## Performance Metrics

### Expected Execution Times

**Fast feedback** (lint + type check): ~2-4 minutes
**Full test matrix**: ~5-10 minutes
**Security scans**: ~2-3 minutes

**Total CI time**: ~10-15 minutes for complete PR validation

### CI Minutes Usage

**Per PR** (~8 jobs in test matrix):

- Ubuntu: ~4 jobs × 3 min = 12 minutes
- macOS: ~2 jobs × 4 min = 8 minutes (2× multiplier)
- Windows: ~2 jobs × 4 min = 8 minutes (2× multiplier)
- Other jobs: ~3 jobs × 2 min = 6 minutes

**Total per PR:** ~34 equivalent minutes
**Monthly (20 PRs):** ~680 minutes (~11.3 hours)

**GitHub Free tier:** 2,000 minutes/month (public repos get unlimited)

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Pre-commit CI Integration](https://pre-commit.ci/)
- [Codecov Documentation](https://docs.codecov.com/)
- [actionlint - Workflow Linter](https://github.com/rhysd/actionlint)
