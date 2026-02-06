"""
Tests for executor module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from roller.config import SeriesConfig
from roller.executor import PatchExecutor
from roller.reporter import Reporter
from roller.repository import RepositoryError


class TestPatchExecutor:
    """Tests for PatchExecutor class."""

    def test_executor_creation(self, sample_series_config: SeriesConfig):
        """Test creating a PatchExecutor instance."""
        reporter = Reporter()
        executor = PatchExecutor(sample_series_config, reporter, exit_on_error=False)

        assert executor.config == sample_series_config
        assert executor.reporter == reporter
        assert executor.exit_on_error is False
        assert executor.workspace is not None

    def test_executor_with_exit_on_error(self, sample_series_config: SeriesConfig):
        """Test creating executor with exit_on_error flag."""
        reporter = Reporter()
        executor = PatchExecutor(sample_series_config, reporter, exit_on_error=True)

        assert executor.exit_on_error is True

    def test_render_commit_message_with_spaces(self):
        """Test rendering commit message with spaces in template."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands="./patch.sh",
            commit_msg="Update {{ project_name }} dependencies"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        message = executor._render_commit_message("my-repo")

        assert message == "Update my-repo dependencies"

    def test_render_commit_message_without_spaces(self):
        """Test rendering commit message without spaces in template."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands="./patch.sh",
            commit_msg="Update {{project_name}} dependencies"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        message = executor._render_commit_message("my-repo")

        assert message == "Update my-repo dependencies"

    def test_render_commit_message_no_template(self):
        """Test rendering commit message with no template variable."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands="./patch.sh",
            commit_msg="Static commit message"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        message = executor._render_commit_message("my-repo")

        assert message == "Static commit message"

    @patch('roller.executor.Repository')
    def test_execute_missing_script(self, mock_repo_class, sample_series_config: SeriesConfig, temp_dir: Path):
        """Test execute with missing patch script."""
        # Update config to point to non-existent script
        sample_series_config.commands = str(temp_dir / "nonexistent.sh")

        reporter = Reporter()
        executor = PatchExecutor(sample_series_config, reporter)

        success = executor.execute()

        assert success is False

    @patch('roller.executor.Repository')
    def test_execute_script_not_file(self, mock_repo_class, sample_series_config: SeriesConfig, temp_dir: Path):
        """Test execute when script path is a directory."""
        # Create a directory instead of a file
        script_dir = temp_dir / "script"
        script_dir.mkdir()
        sample_series_config.commands = str(script_dir)

        reporter = Reporter()
        executor = PatchExecutor(sample_series_config, reporter)

        success = executor.execute()

        assert success is False

    @patch('roller.executor.Repository')
    def test_process_repository_clone_success(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test successful repository processing."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit",
            commit=False  # Don't commit to simplify test
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.return_value = (True, "success", "")
        mock_repo.has_changes.return_value = False  # No changes to commit
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is True
        mock_repo.clone.assert_called_once()
        mock_repo.setup_review.assert_called_once()
        mock_repo.run_command.assert_called_once()

    @patch('roller.executor.Repository')
    def test_process_repository_clone_failure(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing when clone fails."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.side_effect = RepositoryError("Clone failed")
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is False
        assert len(reporter.results) == 1
        assert reporter.results[0]['status'] == 'failed'

    @patch('roller.executor.Repository')
    def test_process_repository_patch_script_failure(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing when patch script fails."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.return_value = (False, "", "script error")
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is False
        assert reporter.results[0]['details'] == 'Patch script failed'

    @patch('roller.executor.Repository')
    def test_process_repository_no_changes(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing when no changes are detected."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.return_value = (True, "", "")
        mock_repo.has_changes.return_value = False
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is True
        assert reporter.results[0]['status'] == 'skipped'
        assert reporter.results[0]['details'] == 'No changes'
        # Commit should not be called
        mock_repo.commit.assert_not_called()

    @patch('roller.executor.Repository')
    def test_process_repository_with_commit(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing with commit enabled."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit for {{ project_name }}",
            commit=True
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "test-repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.return_value = (True, "", "")
        mock_repo.has_changes.return_value = True
        mock_repo.commit.return_value = "abc123d"
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/test-repo.git", 1, 1, executable_script
        )

        assert success is True
        mock_repo.stage_all.assert_called_once()
        mock_repo.commit.assert_called_once_with("Test commit for test-repo")
        assert reporter.results[0]['status'] == 'succeeded'

    @patch('roller.executor.Repository')
    def test_process_repository_with_review(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing with review submission."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit",
            commit=True,
            review=True,
            topic="test-topic"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.return_value = (True, "", "")
        mock_repo.has_changes.return_value = True
        mock_repo.commit.return_value = "abc123d"
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is True
        mock_repo.submit_review.assert_called_once_with("test-topic")

    @patch('roller.executor.Repository')
    def test_process_repository_tests_passing(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing with passing tests."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit",
            run_tests=True,
            test_command="pytest"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.side_effect = [
            (True, "", ""),  # patch script
            (True, "tests passed", "")  # tests
        ]
        mock_repo.has_changes.return_value = True  # Must have changes for tests to run
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is True
        assert mock_repo.run_command.call_count == 2
        # Second call should be the test command
        assert mock_repo.run_command.call_args_list[1][0][0] == "pytest"

    @patch('roller.executor.Repository')
    def test_process_repository_tests_failing_blocking(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing with failing blocking tests."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit",
            run_tests=True,
            tests_blocking=True,
            test_command="pytest"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.side_effect = [
            (True, "", ""),  # patch script
            (False, "", "test failed")  # tests
        ]
        mock_repo.has_changes.return_value = True
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        assert success is False
        assert reporter.results[0]['status'] == 'failed'
        assert 'Tests failed' in reporter.results[0]['details']

    @patch('roller.executor.Repository')
    def test_process_repository_tests_failing_non_blocking(self, mock_repo_class, executable_script: Path, temp_dir: Path):
        """Test repository processing with failing non-blocking tests."""
        config = SeriesConfig(
            projects=["https://github.com/org/repo.git"],
            commands=str(executable_script),
            commit_msg="Test commit",
            run_tests=True,
            tests_blocking=False,
            test_command="pytest"
        )
        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Mock repository instance
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.side_effect = [
            (True, "", ""),  # patch script
            (False, "", "test failed")  # tests
        ]
        mock_repo.has_changes.return_value = False  # Skip commit part
        mock_repo_class.return_value = mock_repo

        success = executor._process_repository(
            "https://github.com/org/repo.git", 1, 1, executable_script
        )

        # Should still succeed with non-blocking tests
        assert success is True
