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

    @patch("subprocess.run")
    def test_clone_success(self, mock_run, temp_dir: Path):
        """Test successful repository cloning."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.clone()

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "clone", repo.url, str(repo.path)]

    @patch("subprocess.run")
    def test_clone_failure(self, mock_run, temp_dir: Path):
        """Test failed repository cloning."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git clone", stderr="fatal: repository not found"
        )
        repo = Repository("https://github.com/org/nonexistent.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to clone"):
            repo.clone()

    @patch("subprocess.run")
    def test_setup_review_success(self, mock_run, temp_dir: Path):
        """Test successful git-review setup."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.setup_review()

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "review", "-s"]
        assert call_args[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_setup_review_failure(self, mock_run, temp_dir: Path):
        """Test failed git-review setup."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git review -s", stderr="git-review not configured"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to setup git-review"):
            repo.setup_review()

    @patch("subprocess.run")
    def test_has_changes_true(self, mock_run, temp_dir: Path):
        """Test detecting uncommitted changes."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout=" M file.txt\n?? new_file.txt\n"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.has_changes()

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "status", "--porcelain"]

    @patch("subprocess.run")
    def test_has_changes_false(self, mock_run, temp_dir: Path):
        """Test detecting no changes."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.has_changes()

        assert result is False

    @patch("subprocess.run")
    def test_has_changes_error(self, mock_run, temp_dir: Path):
        """Test error when checking for changes."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git status", stderr="fatal: not a git repository"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to check status"):
            repo.has_changes()

    @patch("subprocess.run")
    def test_stage_all_success(self, mock_run, temp_dir: Path):
        """Test staging all changes."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.stage_all()

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "add", "-A"]
        assert call_args[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_stage_all_failure(self, mock_run, temp_dir: Path):
        """Test failed staging."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git add", stderr="fatal: error staging files"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to stage changes"):
            repo.stage_all()

    @patch("subprocess.run")
    def test_commit_success(self, mock_run, temp_dir: Path):
        """Test creating a commit."""
        # Mock both the commit and rev-parse commands
        mock_run.side_effect = [
            MagicMock(returncode=0),  # git commit
            MagicMock(returncode=0, stdout="abc123d\n"),  # git rev-parse
        ]
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        commit_hash = repo.commit("Test commit message")

        assert commit_hash == "abc123d"
        assert mock_run.call_count == 2
        # Check commit call
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ["git", "commit", "-s", "-m", "Test commit message"]
        # Check rev-parse call
        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ["git", "rev-parse", "--short", "HEAD"]

    @patch("subprocess.run")
    def test_commit_failure(self, mock_run, temp_dir: Path):
        """Test failed commit."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git commit", stderr="nothing to commit"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to commit"):
            repo.commit("Test commit")

    @patch("subprocess.run")
    def test_submit_review_without_topic(self, mock_run, temp_dir: Path):
        """Test submitting for review without topic."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.submit_review(topic=None)

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "review"]
        assert call_args[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_submit_review_with_topic(self, mock_run, temp_dir: Path):
        """Test submitting for review with topic."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.submit_review(topic="my-topic")

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "review", "-t", "my-topic"]

    @patch("subprocess.run")
    def test_submit_review_failure(self, mock_run, temp_dir: Path):
        """Test failed review submission."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git review", stderr="error: no remote configured"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to submit for review"):
            repo.submit_review()

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run, temp_dir: Path):
        """Test running a command successfully."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="command output", stderr=""
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("echo 'test'")

        assert success is True
        assert stdout == "command output"
        assert stderr == ""
        call_args = mock_run.call_args
        assert call_args[1]["shell"] is True
        assert call_args[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run, temp_dir: Path):
        """Test running a command that fails."""
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="command error"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("false")

        assert success is False
        assert stdout == ""
        assert stderr == "command error"

    @patch("subprocess.run")
    def test_run_command_timeout(self, mock_run, temp_dir: Path):
        """Test running a command that times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 600)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("sleep 1000")

        assert success is False
        assert stdout == ""
        assert "timed out" in stderr

    @patch("subprocess.run")
    def test_run_command_exception(self, mock_run, temp_dir: Path):
        """Test running a command that raises an exception."""
        mock_run.side_effect = Exception("Unexpected error")
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        success, stdout, stderr = repo.run_command("some command")

        assert success is False
        assert stdout == ""
        assert "Unexpected error" in stderr

    @patch("subprocess.run")
    def test_get_current_branch_success(self, mock_run, temp_dir: Path):
        """Test getting current branch name."""
        mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        branch = repo.get_current_branch()

        assert branch == "main"
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        assert call_args[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_get_current_branch_detached_head(self, mock_run, temp_dir: Path):
        """Test getting current branch in detached HEAD state."""
        mock_run.return_value = MagicMock(returncode=0, stdout="HEAD\n")
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        branch = repo.get_current_branch()

        assert branch == ""

    @patch("subprocess.run")
    def test_get_current_branch_failure(self, mock_run, temp_dir: Path):
        """Test failed to get current branch."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git rev-parse", stderr="fatal: not a git repository"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to get current branch"):
            repo.get_current_branch()

    @patch("subprocess.run")
    def test_branch_exists_local(self, mock_run, temp_dir: Path):
        """Test checking if branch exists locally."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.branch_exists("feature-branch")

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "show-ref", "--verify", "refs/heads/feature-branch"]

    @patch("subprocess.run")
    def test_branch_exists_remote(self, mock_run, temp_dir: Path):
        """Test checking if branch exists remotely."""
        # First call returns non-zero (not local), second returns 0 (found remote)
        mock_run.side_effect = [
            MagicMock(returncode=1),
            MagicMock(returncode=0),
        ]
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.branch_exists("feature-branch")

        assert result is True
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_branch_exists_not_found(self, mock_run, temp_dir: Path):
        """Test checking if branch does not exist."""
        mock_run.return_value = MagicMock(returncode=1)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.branch_exists("nonexistent-branch")

        assert result is False

    @patch("subprocess.run")
    def test_create_branch_success(self, mock_run, temp_dir: Path):
        """Test creating a new branch."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.create_branch("new-branch")

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "checkout", "-b", "new-branch"]
        assert call_args[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_create_branch_failure(self, mock_run, temp_dir: Path):
        """Test failed branch creation."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git checkout -b", stderr="fatal: branch already exists"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to create branch"):
            repo.create_branch("existing-branch")

    @patch("subprocess.run")
    def test_branch_exists_locally_true(self, mock_run, temp_dir: Path):
        """Test checking if branch exists locally."""
        mock_run.return_value = MagicMock(returncode=0)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.branch_exists_locally("feature-branch")

        assert result is True
        call_args = mock_run.call_args
        assert call_args[0][0] == ["git", "show-ref", "--verify", "refs/heads/feature-branch"]

    @patch("subprocess.run")
    def test_branch_exists_locally_false(self, mock_run, temp_dir: Path):
        """Test checking if branch doesn't exist locally."""
        mock_run.return_value = MagicMock(returncode=1)
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.branch_exists_locally("nonexistent-branch")

        assert result is False

    @patch("subprocess.run")
    def test_checkout_branch_local_exists(self, mock_run, temp_dir: Path):
        """Test switching to an existing local branch."""
        # First call checks if branch exists locally (returns 0 = exists)
        # Second call checks out the branch
        mock_run.side_effect = [
            MagicMock(returncode=0),  # branch_exists_locally
            MagicMock(returncode=0),  # git checkout
        ]
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.checkout_branch("feature-branch")

        assert result is True
        assert mock_run.call_count == 2
        # Second call should be git checkout
        checkout_call = mock_run.call_args_list[1]
        assert checkout_call[0][0] == ["git", "checkout", "feature-branch"]
        assert checkout_call[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_checkout_branch_remote_only(self, mock_run, temp_dir: Path):
        """Test switching to a branch that only exists remotely."""
        # First call checks if branch exists locally (returns 1 = doesn't exist)
        # Second call creates tracking branch from origin
        mock_run.side_effect = [
            MagicMock(returncode=1),  # branch_exists_locally
            MagicMock(returncode=0),  # git checkout -b
        ]
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.checkout_branch("remote-branch")

        assert result is True
        assert mock_run.call_count == 2
        # Second call should create tracking branch
        checkout_call = mock_run.call_args_list[1]
        assert checkout_call[0][0] == ["git", "checkout", "-b", "remote-branch", "origin/remote-branch"]
        assert checkout_call[1]["cwd"] == repo.path

    @patch("subprocess.run")
    def test_checkout_branch_failure(self, mock_run, temp_dir: Path):
        """Test failed branch checkout when branch doesn't exist anywhere."""
        # First call checks if branch exists locally (returns 1 = doesn't exist)
        # Second call tries to create tracking branch from origin (fails)
        mock_run.side_effect = [
            MagicMock(returncode=1),  # branch_exists_locally
            subprocess.CalledProcessError(
                1, "git checkout", stderr="error: pathspec 'origin/nonexistent' did not match"
            ),
        ]
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        with pytest.raises(RepositoryError, match="Failed to checkout branch"):
            repo.checkout_branch("nonexistent")

    @patch("subprocess.run")
    def test_has_uncommitted_changes(self, mock_run, temp_dir: Path):
        """Test checking for uncommitted changes."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout=" M file.txt\n"
        )
        repo = Repository("https://github.com/org/test-repo.git", temp_dir)

        result = repo.has_uncommitted_changes()

        assert result is True
