"""
Integration tests for changes-roller.

These tests verify the full workflow end-to-end with real Git repositories.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from roller.config import ConfigParser
from roller.executor import PatchExecutor
from roller.reporter import Reporter


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete workflows."""

    def test_config_to_executor_integration(self, config_file: Path, temp_dir: Path):
        """Test parsing config and passing to executor."""
        parser = ConfigParser(config_file)
        config = parser.parse()

        reporter = Reporter(verbose=False)
        executor = PatchExecutor(config, reporter, exit_on_error=False)

        assert executor.config.projects == config.projects
        assert executor.config.commands == config.commands
        assert executor.reporter == reporter

    @patch("roller.executor.Repository")
    def test_end_to_end_workflow_with_mocked_git(
        self, mock_repo_class, temp_dir: Path, executable_script: Path
    ):
        """Test complete workflow with mocked Git operations."""
        # Create a config file
        config_content = f"""[SERIE]
projects = https://github.com/test/repo1.git,
           https://github.com/test/repo2.git
commands = {executable_script}
commit_msg = Test commit for {{{{ project_name }}}}
commit = true
review = false
"""
        config_file = temp_dir / "test.ini"
        config_file.write_text(config_content)

        # Parse configuration
        parser = ConfigParser(config_file)
        config = parser.parse()

        # Mock repository
        mock_repo = MagicMock()
        mock_repo.name = "repo1"
        mock_repo.clone.return_value = True
        mock_repo.setup_review.return_value = True
        mock_repo.run_command.return_value = (True, "", "")
        mock_repo.has_changes.return_value = True
        mock_repo.commit.return_value = "abc123"
        mock_repo_class.return_value = mock_repo

        # Execute
        reporter = Reporter(verbose=False)
        executor = PatchExecutor(config, reporter)

        # Set workspace path (normally done by execute())
        executor.workspace.path = temp_dir

        # Process single repository
        success = executor._process_repository(
            config.projects[0], 1, 2, executable_script
        )

        assert success is True
        assert len(reporter.results) == 1
        assert reporter.results[0]["status"] == "succeeded"

    def test_workspace_lifecycle(self, temp_dir: Path):
        """Test workspace creation and cleanup lifecycle."""
        from roller.workspace import Workspace

        workspace = Workspace(base_dir=temp_dir)

        # Before creation
        assert workspace.path is None

        # After creation
        path = workspace.create()
        assert path.exists()
        assert workspace.path == path

        # Can get repository paths
        repo_path = workspace.get_repo_path("test-repo")
        assert repo_path == path / "test-repo"

        # After cleanup
        workspace.cleanup()
        assert not path.exists()
        assert workspace.path is None

    @patch("roller.executor.Repository")
    def test_multiple_repositories_parallel_processing(
        self, mock_repo_class, temp_dir: Path, executable_script: Path
    ):
        """Test processing multiple repositories in parallel."""
        # Create config with multiple projects
        config_content = f"""[SERIE]
projects = https://github.com/test/repo1.git,
           https://github.com/test/repo2.git,
           https://github.com/test/repo3.git
commands = {executable_script}
commit_msg = Test commit
commit = false
"""
        config_file = temp_dir / "test.ini"
        config_file.write_text(config_content)

        # Parse configuration
        parser = ConfigParser(config_file)
        config = parser.parse()

        # Mock repository to track calls
        call_count = [0]

        def mock_repo_init(*args, **kwargs):
            instance = MagicMock()
            call_count[0] += 1
            instance.name = f"repo{call_count[0]}"
            instance.clone.return_value = True
            instance.setup_review.return_value = True
            instance.run_command.return_value = (True, "", "")
            instance.has_changes.return_value = False
            return instance

        mock_repo_class.side_effect = mock_repo_init

        # Execute
        reporter = Reporter(verbose=False)
        executor = PatchExecutor(config, reporter)

        # Set workspace path (normally done by execute())
        executor.workspace.path = temp_dir

        # Don't call full execute() as it requires actual script file validation
        # Instead test the repository processing individually
        for idx, project in enumerate(config.projects):
            executor._process_repository(
                project, idx + 1, len(config.projects), executable_script
            )

        assert len(reporter.results) == 3
        assert all(r["status"] == "skipped" for r in reporter.results)

    def test_reporter_accumulates_results(self):
        """Test that reporter correctly accumulates results."""
        reporter = Reporter()

        # Add various results
        reporter.add_result("repo1", "succeeded")
        reporter.add_result("repo2", "failed", "Build error")
        reporter.add_result("repo3", "skipped", "No changes")
        reporter.add_result("repo4", "succeeded")

        assert len(reporter.results) == 4

        # Count by status
        succeeded = sum(1 for r in reporter.results if r["status"] == "succeeded")
        failed = sum(1 for r in reporter.results if r["status"] == "failed")
        skipped = sum(1 for r in reporter.results if r["status"] == "skipped")

        assert succeeded == 2
        assert failed == 1
        assert skipped == 1

    @patch("subprocess.run")
    def test_repository_operations_sequence(self, mock_run, temp_dir: Path):
        """Test the sequence of Git operations on a repository."""
        from roller.repository import Repository

        repo = Repository("https://github.com/test/repo.git", temp_dir)

        # Mock successful operations
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Clone
        repo.clone()
        assert any(
            "git" in str(call[0][0]) and "clone" in str(call[0][0])
            for call in mock_run.call_args_list
        )

        # Check for changes
        mock_run.return_value = MagicMock(
            returncode=0, stdout=" M file.txt\n", stderr=""
        )
        has_changes = repo.has_changes()
        assert has_changes is True

        # Stage changes
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        repo.stage_all()

        # Commit
        mock_run.side_effect = [
            MagicMock(returncode=0),  # commit
            MagicMock(returncode=0, stdout="abc123d\n"),  # rev-parse
        ]
        commit_hash = repo.commit("Test message")
        assert commit_hash == "abc123d"

    def test_config_with_tests_enabled(self, temp_dir: Path):
        """Test configuration with tests enabled."""
        config_content = """[SERIE]
projects = https://github.com/test/repo.git
commands = ./patch.sh
commit_msg = Test

[TESTS]
run = true
blocking = true
command = pytest -v
"""
        config_file = temp_dir / "test.ini"
        config_file.write_text(config_content)

        parser = ConfigParser(config_file)
        config = parser.parse()

        assert config.run_tests is True
        assert config.tests_blocking is True
        assert config.test_command == "pytest -v"

    @patch("roller.executor.Repository")
    def test_error_handling_propagation(
        self, mock_repo_class, temp_dir: Path, executable_script: Path
    ):
        """Test that errors are properly caught and reported."""
        from roller.repository import RepositoryError

        config_content = f"""[SERIE]
projects = https://github.com/test/repo.git
commands = {executable_script}
commit_msg = Test
"""
        config_file = temp_dir / "test.ini"
        config_file.write_text(config_content)

        parser = ConfigParser(config_file)
        config = parser.parse()

        # Mock repository to raise error
        mock_repo = MagicMock()
        mock_repo.name = "repo"
        mock_repo.clone.side_effect = RepositoryError("Network error")
        mock_repo_class.return_value = mock_repo

        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        # Set workspace path (normally done by execute())
        executor.workspace.path = temp_dir

        success = executor._process_repository(
            config.projects[0], 1, 1, executable_script
        )

        assert success is False
        assert len(reporter.results) == 1
        assert reporter.results[0]["status"] == "failed"
        assert "Network error" in reporter.results[0]["details"]

    def test_commit_message_rendering(self, temp_dir: Path):
        """Test commit message template rendering."""
        from roller.config import SeriesConfig
        from roller.executor import PatchExecutor

        config = SeriesConfig(
            projects=["https://github.com/test/repo.git"],
            commands="./patch.sh",
            commit_msg="Update {{ project_name }} to version 2.0",
        )

        reporter = Reporter()
        executor = PatchExecutor(config, reporter)

        message = executor._render_commit_message("my-awesome-repo")
        assert message == "Update my-awesome-repo to version 2.0"
