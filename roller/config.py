"""
Configuration file parsing for changes-roller.
"""

import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SeriesConfig:
    """Configuration for a patch series."""

    projects: list[str]
    commands: str
    commit_msg: str
    topic: str = ""
    commit: bool = True
    review: bool = False
    run_tests: bool = False
    tests_blocking: bool = False
    test_command: str = ""
    # Branch switching options
    branch: str | None = None
    create_branch: bool = False
    stay_on_branch: bool = False
    # Command execution options
    pre_commands: list[str] = None  # type: ignore
    post_commands: list[str] = None  # type: ignore
    continue_on_error: bool = False
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Initialize mutable default values."""
        if self.pre_commands is None:
            self.pre_commands = []
        if self.post_commands is None:
            self.post_commands = []


class ConfigParser:
    """Parse INI configuration files for patch series."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._parser = configparser.ConfigParser()

    def parse(self) -> SeriesConfig:
        """Parse the configuration file and return SeriesConfig."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        self._parser.read(self.config_path)

        # Parse SERIE section
        if "SERIE" not in self._parser:
            raise ValueError("Configuration file must contain [SERIE] section")

        serie = self._parser["SERIE"]

        # Parse project list (comma-separated, possibly multi-line)
        projects_str = serie.get("projects", "")
        projects = [p.strip() for p in projects_str.split(",") if p.strip()]

        if not projects:
            raise ValueError("Configuration must specify at least one project")

        commands = serie.get("commands", "")
        if not commands:
            raise ValueError("Configuration must specify commands path")

        commit_msg = serie.get("commit_msg", "")
        if not commit_msg:
            raise ValueError("Configuration must specify commit_msg")

        # Parse optional fields
        topic = serie.get("topic", "")
        commit = serie.getboolean("commit", fallback=True)
        review = serie.getboolean("review", fallback=False)

        # Parse TESTS section if it exists
        run_tests = False
        tests_blocking = False
        test_command = ""

        if "TESTS" in self._parser:
            tests = self._parser["TESTS"]
            run_tests = tests.getboolean("run", fallback=False)
            tests_blocking = tests.getboolean("blocking", fallback=False)
            test_command = tests.get("command", "tox")

        # Parse branch switching options
        branch = serie.get("branch", None)
        create_branch = serie.getboolean("create_branch", fallback=False)
        stay_on_branch = serie.getboolean("stay_on_branch", fallback=False)

        # Parse command execution options
        pre_commands_str = serie.get("pre_commands", "")
        pre_commands = [
            cmd.strip() for cmd in pre_commands_str.split("\n") if cmd.strip()
        ]

        post_commands_str = serie.get("post_commands", "")
        post_commands = [
            cmd.strip() for cmd in post_commands_str.split("\n") if cmd.strip()
        ]

        continue_on_error = serie.getboolean("continue_on_error", fallback=False)
        dry_run = serie.getboolean("dry_run", fallback=False)

        return SeriesConfig(
            projects=projects,
            commands=commands,
            commit_msg=commit_msg,
            topic=topic,
            commit=commit,
            review=review,
            run_tests=run_tests,
            tests_blocking=tests_blocking,
            test_command=test_command,
            branch=branch,
            create_branch=create_branch,
            stay_on_branch=stay_on_branch,
            pre_commands=pre_commands,
            post_commands=post_commands,
            continue_on_error=continue_on_error,
            dry_run=dry_run,
        )
