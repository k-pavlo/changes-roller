"""
Shared pytest fixtures for changes-roller tests.
"""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from roller.config import SeriesConfig


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_content() -> str:
    """Return sample configuration file content."""
    return """[SERIE]
projects = https://github.com/org/repo1.git,
           https://github.com/org/repo2.git
commands = ./patch.sh
commit_msg = Update dependencies in {{ project_name }}
topic = test-topic
commit = true
review = false

[TESTS]
run = true
blocking = false
command = pytest
"""


@pytest.fixture
def minimal_config_content() -> str:
    """Return minimal valid configuration file content."""
    return """[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test commit message
"""


@pytest.fixture
def config_file(temp_dir: Path, sample_config_content: str) -> Path:
    """Create a temporary configuration file."""
    config_path = temp_dir / "series.ini"
    config_path.write_text(sample_config_content)
    return config_path


@pytest.fixture
def minimal_config_file(temp_dir: Path, minimal_config_content: str) -> Path:
    """Create a minimal configuration file."""
    config_path = temp_dir / "minimal.ini"
    config_path.write_text(minimal_config_content)
    return config_path


@pytest.fixture
def sample_series_config() -> SeriesConfig:
    """Return a sample SeriesConfig object."""
    return SeriesConfig(
        projects=[
            "https://github.com/org/repo1.git",
            "https://github.com/org/repo2.git",
        ],
        commands="./patch.sh",
        commit_msg="Update dependencies in {{ project_name }}",
        topic="test-topic",
        commit=True,
        review=False,
        run_tests=True,
        tests_blocking=False,
        test_command="pytest",
    )


@pytest.fixture
def executable_script(temp_dir: Path) -> Path:
    """Create a simple executable script."""
    script_path = temp_dir / "script.sh"
    script_path.write_text("#!/bin/bash\necho 'Hello'\n")
    script_path.chmod(0o755)
    return script_path
