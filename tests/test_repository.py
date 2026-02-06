"""
Tests for repository module.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from roller.repository import Repository, RepositoryError


class TestRepository:
    """Tests for Repository class."""

    def test_repository_creation(self, temp_dir: Path):
        """Test creating a Repository instance."""
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        assert repo.url == "https://github.com/org/test-repo.git"
        assert repo.workspace_path == temp_dir
        assert repo.name == "test-repo"
        assert repo.path == temp_dir / "test-repo"

    def test_extract_repo_name_https(self):
        """Test extracting repository name from HTTPS URL."""
        url = "https://github.com/org/my-repo.git"
        name = Repository._extract_repo_name(url)
        assert name == "my-repo"

    def test_extract_repo_name_ssh(self):
        """Test extracting repository name from SSH URL."""
        url = "git@github.com:org/my-repo.git"
        name = Repository._extract_repo_name(url)
        assert name == "my-repo"

    def test_extract_repo_name_without_git_suffix(self):
        """Test extracting repository name without .git suffix."""
        url = "https://github.com/org/my-repo"
        name = Repository._extract_repo_name(url)
        assert name == "my-repo"

    def test_extract_repo_name_with_trailing_slash(self):
        """Test extracting repository name with trailing slash."""
        url = "https://github.com/org/my-repo.git/"
        name = Repository._extract_repo_name(url)
        assert name == "my-repo"

    @patch('subprocess.run')
    def test_clone_success(self, mock_run, temp_dir: Path):
        """Test successful repository cloning."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.clone()

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'clone', repo.url, str(repo.path)]

    @patch('subprocess.run')
    def test_clone_failure(self, mock_run, temp_dir: Path):
        """Test failed repository cloning."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git clone', stderr="fatal: repository not found"
        )
        repo = Repository("https://github.com/org/nonexistent.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to clone"):
            repo.clone()

    @patch('subprocess.run')
    def test_setup_review_success(self, mock_run, temp_dir: Path):
        """Test successful git-review setup."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.setup_review()

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'review', '-s']
        assert call_args[1]['cwd'] == repo.path

    @patch('subprocess.run')
    def test_setup_review_failure(self, mock_run, temp_dir: Path):
        """Test failed git-review setup."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git review -s', stderr="git-review not configured"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to setup git-review"):
            repo.setup_review()

    @patch('subprocess.run')
    def test_has_changes_true(self, mock_run, temp_dir: Path):
        """Test detecting uncommitted changes."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=" M file.txt\n?? new_file.txt\n"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.has_changes()

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'status', '--porcelain']

    @patch('subprocess.run')
    def test_has_changes_false(self, mock_run, temp_dir: Path):
        """Test detecting no changes."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.has_changes()

        assert result is False

    @patch('subprocess.run')
    def test_has_changes_error(self, mock_run, temp_dir: Path):
        """Test error when checking for changes."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git status', stderr="fatal: not a git repository"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to check status"):
            repo.has_changes()

    @patch('subprocess.run')
    def test_stage_all_success(self, mock_run, temp_dir: Path):
        """Test staging all changes."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.stage_all()

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'add', '-A']
        assert call_args[1]['cwd'] == repo.path

    @patch('subprocess.run')
    def test_stage_all_failure(self, mock_run, temp_dir: Path):
        """Test failed staging."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git add', stderr="fatal: error staging files"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to stage changes"):
            repo.stage_all()

    @patch('subprocess.run')
    def test_commit_success(self, mock_run, temp_dir: Path):
        """Test creating a commit."""
        # Mock both the commit and rev-parse commands
        mock_run.side_effect = [
            MagicMock(returncode=0),  # git commit
            MagicMock(returncode=0, stdout="abc123d\n")  # git rev-parse
        ]
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        commit_hash = repo.commit("Test commit message")

        assert commit_hash == "abc123d"
        assert mock_run.call_count == 2
        # Check commit call
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ['git', 'commit', '-s', '-m', 'Test commit message']
        # Check rev-parse call
        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ['git', 'rev-parse', '--short', 'HEAD']

    @patch('subprocess.run')
    def test_commit_failure(self, mock_run, temp_dir: Path):
        """Test failed commit."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git commit', stderr="nothing to commit"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to commit"):
            repo.commit("Test commit")

    @patch('subprocess.run')
    def test_submit_review_without_topic(self, mock_run, temp_dir: Path):
        """Test submitting for review without topic."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.submit_review(topic=None)

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'review']
        assert call_args[1]['cwd'] == repo.path

    @patch('subprocess.run')
    def test_submit_review_with_topic(self, mock_run, temp_dir: Path):
        """Test submitting for review with topic."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.submit_review(topic="my-topic")

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ['git', 'review', '-t', 'my-topic']

    @patch('subprocess.run')
    def test_submit_review_failure(self, mock_run, temp_dir: Path):
        """Test failed review submission."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, 'git review', stderr="error: no remote configured"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to submit for review"):
            repo.submit_review()

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run, temp_dir: Path):
        """Test running a command successfully."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="command output",
            stderr=""
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("echo 'test'")

        assert success is True
        assert stdout == "command output"
        assert stderr == ""
        call_args = mock_run.call_args
        assert call_args[1]['shell'] is True
        assert call_args[1]['cwd'] == repo.path

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run, temp_dir: Path):
        """Test running a command that fails."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="command error"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("false")

        assert success is False
        assert stdout == ""
        assert stderr == "command error"

    @patch('subprocess.run')
    def test_run_command_timeout(self, mock_run, temp_dir: Path):
        """Test running a command that times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 600)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("sleep 1000")

        assert success is False
        assert stdout == ""
        assert "timed out" in stderr

    @patch('subprocess.run')
    def test_run_command_exception(self, mock_run, temp_dir: Path):
        """Test running a command that raises an exception."""
        mock_run.side_effect = Exception("Unexpected error")
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("some command")

        assert success is False
        assert stdout == ""
        assert "Unexpected error" in stderr
