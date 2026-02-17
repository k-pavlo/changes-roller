# Examples

This page provides practical examples for common use cases.

## Example 1: Security Update

Apply a security patch across all microservices.

**Patch script (`security-fix.sh`):**

```bash
#!/bin/bash
# Fix security vulnerability in auth module

# Update vulnerable dependency
sed -i 's/auth-lib==1.0.0/auth-lib==1.0.1/' requirements.txt

# Apply code fix
sed -i 's/validate_unsafe/validate_secure/g' src/auth.py

exit 0
```

**Configuration (`security-fix.ini`):**

```ini
[SERIE]
projects = https://github.com/org/api-gateway,
           https://github.com/org/user-service,
           https://github.com/org/payment-service

commands = ./security-fix.sh

commit_msg = Fix authentication vulnerability CVE-2025-1234

             Updates auth-lib to 1.0.1 and replaces unsafe
             validation with secure validation method.

             Security-Bug: CVE-2025-1234

topic = security-cve-2025-1234
commit = true
review = true

[TESTS]
run = true
blocking = true
command = pytest tests/security/
```

**Execute:**

```bash
# Test first
roller create --config-file security-fix.ini --dry-run

# Apply
roller create --config-file security-fix.ini
```

## Example 2: Dependency Upgrade

Update a shared library across all projects.

**Patch script (`update-deps.sh`):**

```bash
#!/bin/bash
# Update shared library to latest version

# Update in requirements.txt
if [ -f requirements.txt ]; then
    sed -i 's/shared-lib==2.0.*/shared-lib==3.0.0/' requirements.txt
fi

# Update in pyproject.toml
if [ -f pyproject.toml ]; then
    sed -i 's/"shared-lib>=2.0"/"shared-lib>=3.0"/' pyproject.toml
fi

exit 0
```

**Configuration (`upgrade-lib.ini`):**

```ini
[SERIE]
projects = https://github.com/org/web-app,
           https://github.com/org/mobile-backend,
           https://github.com/org/analytics-engine

commands = ./update-deps.sh

commit_msg = Upgrade shared-lib to 3.0.0

             Upgrades to latest version for improved performance
             and new API features.

topic = shared-lib-upgrade
commit = true
review = false

[TESTS]
run = true
blocking = false
command = pip install -e . && pytest
```

## Example 3: Multi-Branch Backport

Apply a fix to multiple stable branches.

**Patch script (`hotfix.sh`):**

```bash
#!/bin/bash
# Apply critical bugfix

sed -i 's/if user:/if user is not None:/' src/models.py

exit 0
```

**Execute:**

```bash
# Apply to each stable branch
for branch in stable/2023.1 stable/2024.1 stable/2024.2; do
    roller create --config-file hotfix.ini \
        --branch "$branch" \
        --pre-command "git pull origin $branch" \
        --post-command "git push origin $branch"
done
```

## Example 4: License Header Update

Add or update license headers in source files.

**Patch script (`add-license.sh`):**

```bash
#!/bin/bash
# Add MIT license header to Python files

HEADER="# Copyright 2025 Example Corp
# SPDX-License-Identifier: MIT
"

for file in $(find . -name "*.py" -not -path "*/venv/*"); do
    if ! grep -q "SPDX-License-Identifier" "$file"; then
        echo "$HEADER" | cat - "$file" > temp && mv temp "$file"
    fi
done

exit 0
```

**Configuration (`license-update.ini`):**

```ini
[SERIE]
projects = https://github.com/org/project1,
           https://github.com/org/project2

commands = ./add-license.sh

commit_msg = Add SPDX license headers

             Adds MIT license headers to all Python source files
             for compliance with open source requirements.

topic = license-compliance
commit = true
review = true
```

## Example 5: Configuration Migration

Migrate configuration files to new format.

**Patch script (`migrate-config.sh`):**

```bash
#!/bin/bash
# Migrate from YAML to TOML configuration

if [ -f config.yaml ]; then
    # Convert YAML to TOML (using a conversion tool)
    python3 -c "
import yaml
import toml

with open('config.yaml') as f:
    data = yaml.safe_load(f)

with open('config.toml', 'w') as f:
    toml.dump(data, f)
"

    # Remove old YAML file
    git rm config.yaml
    git add config.toml
fi

exit 0
```

**Configuration (`config-migration.ini`):**

```ini
[SERIE]
projects = https://github.com/org/app1,
           https://github.com/org/app2

commands = ./migrate-config.sh

commit_msg = Migrate from YAML to TOML configuration

             Converts config.yaml to config.toml using the
             new standardized configuration format.

topic = config-toml-migration
commit = true
review = true

pre_commands = pip install pyyaml toml
```

## Example 6: API Migration

Update API calls to new version.

**Patch script (`api-v2-migration.sh`):**

```bash
#!/bin/bash
# Migrate from API v1 to v2

# Update import statements
find . -name "*.py" -exec sed -i \
    's/from api.v1 import/from api.v2 import/g' {} \;

# Update endpoint URLs
find . -name "*.py" -exec sed -i \
    's|/api/v1/|/api/v2/|g' {} \;

# Update method calls
find . -name "*.py" -exec sed -i \
    's/client.get_user(/client.get_user_profile(/g' {} \;

exit 0
```

**Configuration (`api-migration.ini`):**

```ini
[SERIE]
projects = https://github.com/org/client-lib-python,
           https://github.com/org/client-lib-nodejs

commands = ./api-v2-migration.sh

commit_msg = Migrate to API v2

             Updates all API calls from v1 to v2 endpoints.
             Changes include updated import paths and
             renamed methods.

             Refs: #456

topic = api-v2-migration
commit = true
review = true

[TESTS]
run = true
blocking = true
command = pytest tests/integration/
```

## Example 7: Code Formatting

Apply consistent code formatting across repositories.

**Patch script (`format-code.sh`):**

```bash
#!/bin/bash
# Apply consistent code formatting

# Python files
if command -v ruff &> /dev/null; then
    ruff format .
    ruff check --fix .
fi

# JavaScript files
if [ -f package.json ] && command -v prettier &> /dev/null; then
    prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"
fi

exit 0
```

**Configuration (`formatting.ini`):**

```ini
[SERIE]
projects = https://github.com/org/service-a,
           https://github.com/org/service-b

commands = ./format-code.sh

commit_msg = Apply consistent code formatting

             Applies Ruff formatting for Python and Prettier
             for JavaScript to ensure consistent code style.

topic = code-formatting
commit = true
review = true

pre_commands = pip install ruff
               npm install -g prettier

continue_on_error = false
```

## Example 8: CI/CD Configuration Update

Update GitHub Actions workflow across repositories.

**Patch script (`update-ci.sh`):**

```bash
#!/bin/bash
# Update GitHub Actions to use latest versions

if [ -f .github/workflows/ci.yml ]; then
    # Update actions/checkout version
    sed -i 's/actions\/checkout@v3/actions\/checkout@v4/g' .github/workflows/ci.yml

    # Update actions/setup-python version
    sed -i 's/actions\/setup-python@v4/actions\/setup-python@v5/g' .github/workflows/ci.yml
fi

exit 0
```

**Configuration (`ci-update.ini`):**

```ini
[SERIE]
projects = https://github.com/org/project1,
           https://github.com/org/project2,
           https://github.com/org/project3

commands = ./update-ci.sh

commit_msg = Update GitHub Actions to latest versions

             Updates checkout and setup-python actions to
             latest major versions.

topic = ci-actions-update
commit = true
review = false

post_commands = git push origin main
```

## Example 9: Dry Run and Validation

Preview changes without committing.

```bash
# Test the patch script on one repository
roller create --config-file test.ini --dry-run --verbose

# Review what would happen
# If satisfied, run without dry-run
roller create --config-file test.ini
```

## Example 10: Emergency Rollback

Revert a previous change across repositories.

**Patch script (`rollback.sh`):**

```bash
#!/bin/bash
# Revert previous change

git revert HEAD --no-edit

exit 0
```

```bash
roller create --config-file rollback.ini \
    --pre-command "git pull origin main" \
    --post-command "git push origin main" \
    --exit-on-error
```

## Tips and Best Practices

1. **Test scripts independently** - Run your patch script manually on a test repository first
2. **Use version control** - Keep your patch scripts and configurations in Git
3. **Start small** - Test with a subset of repositories before running on all
4. **Use dry-run** - Always preview with `--dry-run` first
5. **Enable verbose mode** - Use `--verbose` for detailed output during debugging
6. **Handle errors gracefully** - Make scripts idempotent (safe to run multiple times)
7. **Validate changes** - Use tests to verify patches apply correctly
8. **Document intent** - Write clear commit messages explaining the "why"

## More Examples

For complete, runnable examples with all files, see the `examples/` directory in the repository:

- [Dependency Update Example](https://github.com/k-pavlo/changes-roller/tree/main/examples/dependency-update)
- More examples coming soon!
