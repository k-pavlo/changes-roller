## Description

<!-- Provide a clear and concise description of your changes -->

## Related Issues

<!-- Link related issues using #issue_number (e.g., Fixes #123, Closes #456) -->

Fixes #

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Code quality improvement (refactoring, type hints, tests)
- [ ] CI/CD or tooling change

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Testing

<!-- Describe the testing you've performed -->

### Test Environment

- Python version:
- Operating System:
- Git version:

### Test Cases

<!-- Describe test cases or provide commands to test the changes -->

```bash
# Example commands to test the changes
roller create --config-file test.ini
```

## Checklist

<!-- Mark completed items with an 'x' -->

### Code Quality

- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) guide
- [ ] My code follows the project's code style (Ruff formatting)
- [ ] I have run `ruff format .` to format my code
- [ ] I have run `ruff check .` and fixed all linting issues
- [ ] I have run `mypy roller/` and fixed all type errors
- [ ] I have added type hints to all new functions

### Testing

- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have run `pytest` and all tests pass
- [ ] I have maintained or improved code coverage
- [ ] I have tested on multiple platforms (if applicable)

### Documentation

- [ ] I have updated the documentation (README, USAGE, SPECIFICATION)
- [ ] I have added docstrings to new functions and classes
- [ ] I have updated the CHANGELOG.md under `[Unreleased]`
- [ ] I have updated CLI help text (if applicable)
- [ ] I have added or updated examples (if applicable)

### Security

- [ ] My changes don't introduce security vulnerabilities
- [ ] I have run `bandit` security checks (if applicable)
- [ ] I have considered input validation and error handling

### Git

- [ ] My commits have clear, descriptive messages
- [ ] I have rebased my branch on the latest main (if needed)
- [ ] I have squashed commits where appropriate

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->

<!-- Include migration guide for users if applicable -->

## Screenshots or Examples

<!-- If applicable, add screenshots, configuration examples, or command output -->

```bash
# Example usage after this PR

```

## Additional Notes

<!-- Any additional information that reviewers should know -->

## Reviewer Checklist

<!-- For maintainers reviewing this PR -->

- [ ] Code quality meets project standards
- [ ] Tests are comprehensive and passing
- [ ] Documentation is clear and complete
- [ ] CHANGELOG.md is updated appropriately
- [ ] No security concerns
- [ ] Breaking changes are documented and justified
