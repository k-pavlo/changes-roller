"""
Tests for config module.
"""

from pathlib import Path

import pytest

from roller.config import ConfigParser, SeriesConfig


class TestConfigParser:
    """Tests for ConfigParser class."""

    def test_parse_valid_config(self, config_file: Path):
        """Test parsing a valid configuration file."""
        parser = ConfigParser(config_file)
        config = parser.parse()

        assert isinstance(config, SeriesConfig)
        assert len(config.projects) == 2
        assert config.projects[0] == "https://github.com/org/repo1.git"
        assert config.projects[1] == "https://github.com/org/repo2.git"
        assert config.commands == "./patch.sh"
        assert config.commit_msg == "Update dependencies in {{ project_name }}"
        assert config.topic == "test-topic"
        assert config.commit is True
        assert config.review is False
        assert config.run_tests is True
        assert config.tests_blocking is False
        assert config.test_command == "pytest"

    def test_parse_minimal_config(self, minimal_config_file: Path):
        """Test parsing a minimal configuration file."""
        parser = ConfigParser(minimal_config_file)
        config = parser.parse()

        assert len(config.projects) == 1
        assert config.projects[0] == "https://github.com/org/repo.git"
        assert config.commands == "./patch.sh"
        assert config.commit_msg == "Test commit message"
        # Check defaults
        assert config.topic == ""
        assert config.commit is True
        assert config.review is False
        assert config.run_tests is False
        assert config.tests_blocking is False
        assert config.test_command == ""

    def test_parse_missing_file(self, temp_dir: Path):
        """Test parsing a non-existent configuration file."""
        missing_file = temp_dir / "missing.ini"
        parser = ConfigParser(missing_file)

        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            parser.parse()

    def test_parse_missing_serie_section(self, temp_dir: Path):
        """Test parsing a config file without SERIE section."""
        config_path = temp_dir / "bad.ini"
        config_path.write_text("[OTHER]\nkey = value\n")
        parser = ConfigParser(config_path)

        with pytest.raises(ValueError, match="must contain \\[SERIE\\] section"):
            parser.parse()

    def test_parse_missing_projects(self, temp_dir: Path):
        """Test parsing a config file without projects."""
        config_path = temp_dir / "bad.ini"
        config_path.write_text("""[SERIE]
commands = ./patch.sh
commit_msg = Test
""")
        parser = ConfigParser(config_path)

        with pytest.raises(ValueError, match="must specify at least one project"):
            parser.parse()

    def test_parse_empty_projects(self, temp_dir: Path):
        """Test parsing a config file with empty projects."""
        config_path = temp_dir / "bad.ini"
        config_path.write_text("""[SERIE]
projects =
commands = ./patch.sh
commit_msg = Test
""")
        parser = ConfigParser(config_path)

        with pytest.raises(ValueError, match="must specify at least one project"):
            parser.parse()

    def test_parse_missing_commands(self, temp_dir: Path):
        """Test parsing a config file without commands."""
        config_path = temp_dir / "bad.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commit_msg = Test
""")
        parser = ConfigParser(config_path)

        with pytest.raises(ValueError, match="must specify commands path"):
            parser.parse()

    def test_parse_missing_commit_msg(self, temp_dir: Path):
        """Test parsing a config file without commit_msg."""
        config_path = temp_dir / "bad.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
""")
        parser = ConfigParser(config_path)

        with pytest.raises(ValueError, match="must specify commit_msg"):
            parser.parse()

    def test_parse_multiline_projects(self, temp_dir: Path):
        """Test parsing projects spanning multiple lines."""
        config_path = temp_dir / "multiline.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo1.git,
           https://github.com/org/repo2.git,
           https://github.com/org/repo3.git
commands = ./patch.sh
commit_msg = Test
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert len(config.projects) == 3
        assert config.projects[2] == "https://github.com/org/repo3.git"

    def test_parse_boolean_values(self, temp_dir: Path):
        """Test parsing boolean configuration values."""
        config_path = temp_dir / "bool.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
commit = false
review = true

[TESTS]
run = yes
blocking = no
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.commit is False
        assert config.review is True
        assert config.run_tests is True
        assert config.tests_blocking is False

    def test_parse_tests_section_with_defaults(self, temp_dir: Path):
        """Test parsing TESTS section with default values."""
        config_path = temp_dir / "tests.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test

[TESTS]
command = tox
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.run_tests is False
        assert config.tests_blocking is False
        assert config.test_command == "tox"


class TestSeriesConfig:
    """Tests for SeriesConfig dataclass."""

    def test_series_config_creation(self):
        """Test creating a SeriesConfig instance."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands="./patch.sh",
            commit_msg="Test commit",
        )

        assert config.projects == ["https://github.com/org/repo.git"]
        assert config.commands == "./patch.sh"
        assert config.commit_msg == "Test commit"
        # Check defaults
        assert config.topic == ""
        assert config.commit is True
        assert config.review is False
        assert config.run_tests is False
        assert config.tests_blocking is False
        assert config.test_command == ""

    def test_series_config_with_all_fields(self, sample_series_config: SeriesConfig):
        """Test SeriesConfig with all fields set."""
        assert sample_series_config.topic == "test-topic"
        assert sample_series_config.commit is True
        assert sample_series_config.review is False
        assert sample_series_config.run_tests is True
        assert sample_series_config.tests_blocking is False
        assert sample_series_config.test_command == "pytest"

    def test_series_config_default_lists(self):
        """Test that pre_commands and post_commands default to empty lists."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands="./patch.sh",
            commit_msg="Test commit",
        )

        assert config.pre_commands == []
        assert config.post_commands == []

    def test_parse_branch_options(self, temp_dir: Path):
        """Test parsing branch switching options."""
        config_path = temp_dir / "branch.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
branch = stable/1.x
create_branch = true
stay_on_branch = yes
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.branch == "stable/1.x"
        assert config.create_branch is True
        assert config.stay_on_branch is True

    def test_parse_pre_commands(self, temp_dir: Path):
        """Test parsing pre-commands from config file."""
        config_path = temp_dir / "pre_cmd.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
pre_commands = git pull origin main
               pytest tests/
               echo "Ready"
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert len(config.pre_commands) == 3
        assert config.pre_commands[0] == "git pull origin main"
        assert config.pre_commands[1] == "pytest tests/"
        assert config.pre_commands[2] == 'echo "Ready"'

    def test_parse_post_commands(self, temp_dir: Path):
        """Test parsing post-commands from config file."""
        config_path = temp_dir / "post_cmd.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
post_commands = git add -A
                git commit -m "Auto-commit"
                git push
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert len(config.post_commands) == 3
        assert config.post_commands[0] == "git add -A"
        assert config.post_commands[1] == 'git commit -m "Auto-commit"'
        assert config.post_commands[2] == "git push"

    def test_parse_empty_pre_commands(self, temp_dir: Path):
        """Test parsing empty pre_commands."""
        config_path = temp_dir / "empty_pre.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
pre_commands =
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.pre_commands == []

    def test_parse_continue_on_error(self, temp_dir: Path):
        """Test parsing continue_on_error option."""
        config_path = temp_dir / "continue.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
continue_on_error = true
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.continue_on_error is True

    def test_parse_dry_run(self, temp_dir: Path):
        """Test parsing dry_run option."""
        config_path = temp_dir / "dry_run.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
dry_run = yes
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.dry_run is True

    def test_parse_all_new_options(self, temp_dir: Path):
        """Test parsing all new options together."""
        config_path = temp_dir / "all_new.ini"
        config_path.write_text("""[SERIE]
projects = https://github.com/org/repo.git
commands = ./patch.sh
commit_msg = Test
branch = feature/new
create_branch = yes
stay_on_branch = no
pre_commands = echo "Starting"
               git status
post_commands = echo "Done"
continue_on_error = false
dry_run = true
""")
        parser = ConfigParser(config_path)
        config = parser.parse()

        assert config.branch == "feature/new"
        assert config.create_branch is True
        assert config.stay_on_branch is False
        assert len(config.pre_commands) == 2
        assert len(config.post_commands) == 1
        assert config.continue_on_error is False
        assert config.dry_run is True
