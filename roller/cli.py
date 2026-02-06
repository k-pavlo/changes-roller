"""
Command-line interface for changes-roller.
"""

import sys
from pathlib import Path

import click

from .config import ConfigParser
from .executor import PatchExecutor
from .reporter import Reporter


@click.group()
@click.version_option(version="0.1.0", prog_name="roller")
def cli() -> None:
    """
    changes-roller: A tool for creating and managing coordinated patch series
    across multiple Git repositories.
    """
    pass


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="series.ini",
    help="Output file path (default: series.ini)",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing file")
def init(output: Path, force: bool) -> None:
    """
    Generate a template configuration file.

    Creates a new configuration file with all available options documented
    and example values. Edit this file to customize your patch series.

    Example:
        roller init
        roller init --output my-series.ini
        roller init --output config.ini --force
    """
    # Check if file already exists
    if output.exists() and not force:
        click.echo(
            f"Error: File '{output}' already exists. Use --force to overwrite.",
            err=True,
        )
        sys.exit(1)

    # Template configuration
    template = """# changes-roller Configuration File
# This file defines a patch series to apply across multiple repositories

[SERIE]
# List of Git repository URLs (comma-separated, can span multiple lines)
# Examples:
#   - https://github.com/org/repo.git
#   - git@github.com:org/repo.git
#   - /path/to/local/repo
projects = https://github.com/org/repo1,
           https://github.com/org/repo2,
           https://github.com/org/repo3

# Path to the patch script (must be executable)
# This script will be executed in each repository's directory
commands = ./patch.sh

# Commit message template
# Use {{ project_name }} to insert the repository name
commit_msg = Update dependencies in {{ project_name }}

             This patch updates the project dependencies to their
             latest versions for improved security and performance.

# Optional: Gerrit topic for grouping related patches
# Leave empty if not using Gerrit
topic = dependency-updates-2025

# Automatically commit changes (default: true)
# Set to false to only apply patches without committing
commit = true

# Submit to Gerrit for code review (default: false)
# Requires git-review to be installed and configured
review = false

[TESTS]
# Run tests before committing (default: false)
run = false

# Fail the patch if tests fail (default: false)
# - true: Tests must pass for commit to be created
# - false: Tests run but failures are warnings only
blocking = false

# Command to execute for running tests (default: tox)
# Examples: tox, pytest, npm test, make test, ./run_tests.sh
command = tox
"""

    try:
        output.write_text(template)
        click.echo(f"Created configuration file: {output}")
        click.echo("\nNext steps:")
        click.echo(f"  1. Edit {output} to customize your patch series")
        click.echo("  2. Create your patch script (e.g., patch.sh)")
        click.echo(f"  3. Run: roller create --config-file {output}")
    except Exception as e:
        click.echo(f"Error creating file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to configuration file",
)
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Additional directory for config files (optional)",
)
@click.option(
    "-e", "--exit-on-error", is_flag=True, help="Exit immediately on first failure"
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
def create(
    config_file: Path, config_dir: Path, exit_on_error: bool, verbose: bool
) -> None:
    """
    Create a new patch series across multiple repositories.

    This command reads a configuration file, clones the specified repositories,
    applies patch scripts, runs tests, creates commits, and optionally submits
    them for code review.

    Example:
        roller create --config-file my-series.ini
    """
    try:
        # Parse configuration
        parser = ConfigParser(config_file)
        config = parser.parse()

        # Create reporter
        reporter = Reporter(verbose=verbose)

        # Execute patch series
        executor = PatchExecutor(config, reporter, exit_on_error)
        success = executor.execute()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli()
