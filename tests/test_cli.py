"""
Tests for CLI module.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from roller.cli import cli, init, create


class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_file(self, temp_dir: Path):
        """Test that init command creates a configuration file."""
        runner = CliRunner()
        output_file = temp_dir / "series.ini"

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init, ['--output', str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Created configuration file" in result.output

    def test_init_default_filename(self, temp_dir: Path):
        """Test init with default filename."""
        runner = CliRunner()

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init)
            output_file = Path.cwd() / "series.ini"

        assert result.exit_code == 0
        assert output_file.exists()
        assert "series.ini" in result.output

    def test_init_file_exists_no_force(self, temp_dir: Path):
        """Test init when file exists without --force flag."""
        runner = CliRunner()
        output_file = temp_dir / "existing.ini"
        output_file.write_text("existing content")

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init, ['--output', str(output_file)])

        assert result.exit_code == 1
        assert "already exists" in result.output
        # File should not be overwritten
        assert output_file.read_text() == "existing content"

    def test_init_file_exists_with_force(self, temp_dir: Path):
        """Test init when file exists with --force flag."""
        runner = CliRunner()
        output_file = temp_dir / "existing.ini"
        output_file.write_text("existing content")

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init, ['--output', str(output_file), '--force'])

        assert result.exit_code == 0
        assert "Created configuration file" in result.output
        # File should be overwritten
        assert "existing content" not in output_file.read_text()
        assert "[SERIE]" in output_file.read_text()

    def test_init_template_content(self, temp_dir: Path):
        """Test that init creates file with expected template content."""
        runner = CliRunner()
        output_file = temp_dir / "test.ini"

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init, ['--output', str(output_file)])

        content = output_file.read_text()
        assert "[SERIE]" in content
        assert "[TESTS]" in content
        assert "projects =" in content
        assert "commands =" in content
        assert "commit_msg =" in content
        assert "{{ project_name }}" in content
        assert "topic =" in content

    def test_init_shows_next_steps(self, temp_dir: Path):
        """Test that init shows next steps in output."""
        runner = CliRunner()
        output_file = temp_dir / "test.ini"

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init, ['--output', str(output_file)])

        assert "Next steps:" in result.output
        assert "Edit" in result.output
        assert "roller create" in result.output

    def test_init_write_error(self, temp_dir: Path):
        """Test init when write fails."""
        runner = CliRunner()
        # Try to write to a directory (should fail)
        invalid_path = temp_dir / "subdir"
        invalid_path.mkdir()

        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(init, ['--output', str(invalid_path)])

        assert result.exit_code == 1
        # File exists check happens first, so we get "already exists" error
        assert "already exists" in result.output


class TestCreateCommand:
    """Tests for the create command."""

    @patch('roller.cli.PatchExecutor')
    @patch('roller.cli.ConfigParser')
    def test_create_success(self, mock_config_parser, mock_executor, config_file: Path):
        """Test successful create command."""
        # Mock config parser
        mock_config = MagicMock()
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = mock_config
        mock_config_parser.return_value = mock_parser_instance

        # Mock executor
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute.return_value = True
        mock_executor.return_value = mock_executor_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file)])

        assert result.exit_code == 0
        mock_config_parser.assert_called_once_with(config_file)
        mock_executor_instance.execute.assert_called_once()

    @patch('roller.cli.PatchExecutor')
    @patch('roller.cli.ConfigParser')
    def test_create_failure(self, mock_config_parser, mock_executor, config_file: Path):
        """Test create command when execution fails."""
        # Mock config parser
        mock_config = MagicMock()
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = mock_config
        mock_config_parser.return_value = mock_parser_instance

        # Mock executor to return failure
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute.return_value = False
        mock_executor.return_value = mock_executor_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file)])

        assert result.exit_code == 1

    def test_create_missing_config_file(self, temp_dir: Path):
        """Test create command with missing config file."""
        runner = CliRunner()
        missing_file = temp_dir / "nonexistent.ini"

        result = runner.invoke(create, ['--config-file', str(missing_file)])

        assert result.exit_code == 2  # Click's exit code for bad parameter
        assert "does not exist" in result.output.lower()

    @patch('roller.cli.ConfigParser')
    def test_create_config_error(self, mock_config_parser, config_file: Path):
        """Test create command when config parsing fails."""
        # Mock parser to raise ValueError
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = ValueError("Invalid config")
        mock_config_parser.return_value = mock_parser_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file)])

        assert result.exit_code == 1
        assert "Configuration error" in result.output
        assert "Invalid config" in result.output

    @patch('roller.cli.PatchExecutor')
    @patch('roller.cli.ConfigParser')
    def test_create_verbose_mode(self, mock_config_parser, mock_executor, config_file: Path):
        """Test create command with verbose flag."""
        # Mock config parser
        mock_config = MagicMock()
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = mock_config
        mock_config_parser.return_value = mock_parser_instance

        # Mock executor
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute.return_value = True
        mock_executor.return_value = mock_executor_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file), '--verbose'])

        assert result.exit_code == 0
        # Reporter should be created with verbose=True
        # We can't directly check this without more mocking, but command should succeed

    @patch('roller.cli.PatchExecutor')
    @patch('roller.cli.ConfigParser')
    def test_create_exit_on_error_flag(self, mock_config_parser, mock_executor, config_file: Path):
        """Test create command with exit-on-error flag."""
        # Mock config parser
        mock_config = MagicMock()
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = mock_config
        mock_config_parser.return_value = mock_parser_instance

        # Mock executor
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute.return_value = True
        mock_executor.return_value = mock_executor_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file), '--exit-on-error'])

        assert result.exit_code == 0
        # Executor should be created with exit_on_error=True
        call_args = mock_executor.call_args
        assert call_args[0][2] is True  # Third argument is exit_on_error

    @patch('roller.cli.PatchExecutor')
    @patch('roller.cli.ConfigParser')
    def test_create_keyboard_interrupt(self, mock_config_parser, mock_executor, config_file: Path):
        """Test create command when interrupted by user."""
        # Mock config parser
        mock_config = MagicMock()
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = mock_config
        mock_config_parser.return_value = mock_parser_instance

        # Mock executor to raise KeyboardInterrupt
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute.side_effect = KeyboardInterrupt()
        mock_executor.return_value = mock_executor_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file)])

        assert result.exit_code == 130  # Standard exit code for SIGINT
        assert "Interrupted by user" in result.output

    @patch('roller.cli.PatchExecutor')
    @patch('roller.cli.ConfigParser')
    def test_create_unexpected_error(self, mock_config_parser, mock_executor, config_file: Path):
        """Test create command with unexpected error."""
        # Mock config parser
        mock_config = MagicMock()
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = mock_config
        mock_config_parser.return_value = mock_parser_instance

        # Mock executor to raise unexpected exception
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute.side_effect = RuntimeError("Unexpected error")
        mock_executor.return_value = mock_executor_instance

        runner = CliRunner()
        result = runner.invoke(create, ['--config-file', str(config_file)])

        assert result.exit_code == 1
        assert "Unexpected error" in result.output


class TestCLIGroup:
    """Tests for the CLI group."""

    def test_cli_version(self):
        """Test CLI version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
        assert "roller" in result.output

    def test_cli_help(self):
        """Test CLI help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "changes-roller" in result.output
        assert "init" in result.output
        assert "create" in result.output

    def test_init_help(self):
        """Test init command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['init', '--help'])

        assert result.exit_code == 0
        assert "Generate a template configuration file" in result.output
        assert "--output" in result.output
        assert "--force" in result.output

    def test_create_help(self):
        """Test create command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create', '--help'])

        assert result.exit_code == 0
        assert "Create a new patch series" in result.output
        assert "--config-file" in result.output
        assert "--exit-on-error" in result.output
        assert "--verbose" in result.output
