changes-roller Documentation
============================

**Stop manually patching dozens of repositories. Automate it.**

changes-roller is a command-line tool for creating and managing coordinated
patch series across multiple Git repositories simultaneously.

Perfect for security updates, dependency upgrades, API migrations, license header
updates, configuration standardization, and any scenario requiring identical changes
across multiple repositories.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   overview
   installation
   quick-start

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   usage
   configuration
   examples
   specification

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   autoapi/index

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   changelog
   security

.. toctree::
   :maxdepth: 1
   :caption: Community

   code-of-conduct

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Features
========

* Apply patches to multiple Git repositories in parallel
* Custom patch scripts with full repository access
* Automated Git operations (clone, commit, stage)
* **Git branch switching** - Apply changes to specific branches (e.g., stable branches)
* **Custom command execution** - Run commands before/after applying changes
* **Dry-run mode** - Preview operations without executing them
* Automatic commit sign-off (Signed-off-by line)
* Automatic git-review setup for Gerrit integration
* Commit message templating with variables
* Gerrit code review integration with topic grouping
* Optional test execution before committing
* Clear progress reporting and error handling

Quick Links
===========

* `GitHub Repository <https://github.com/k-pavlo/changes-roller>`_
* `Issue Tracker <https://github.com/k-pavlo/changes-roller/issues>`_
* `PyPI Package <https://pypi.org/project/changes-roller/>`_
* `Changelog <https://github.com/k-pavlo/changes-roller/blob/main/CHANGELOG.md>`_

Project Status
==============

This project maintains high quality standards through automated testing and continuous integration:

* **128 tests** with >90% code coverage
* **Multi-platform testing** across Python 3.10-3.13 on Linux, macOS, and Windows
* **Automated quality checks** including strict type checking (MyPy), linting (Ruff), and security scanning (Bandit)
* **Pre-commit hooks** enforce code quality before commits
* **Continuous security monitoring** with pip-audit and dependency review

All pull requests undergo comprehensive automated testing to ensure reliability and maintainability.

Requirements
============

* Python 3.10 or higher
* Git command-line client
* git-review (optional, for Gerrit integration)

License
=======

This project is licensed under the MIT License.
