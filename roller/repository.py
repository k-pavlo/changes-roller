"""
Repository operations for changes-roller.
"""

import subprocess
from pathlib import Path


class RepositoryError(Exception):
    """Exception raised for repository operation errors."""

    pass


class Repository:
    """Handles Git repository operations."""

    def __init__(self, url: str, workspace_path: Path):
        self.url = url
        self.workspace_path = workspace_path
        self.name = self._extract_repo_name(url)
        self.path = workspace_path / self.name

    @staticmethod
    def _extract_repo_name(url: str) -> str:
        """Extract repository name from URL."""
        # Handle both HTTP and SSH URLs
        # e.g., https://github.com/org/repo.git -> repo
        # e.g., git@github.com:org/repo.git -> repo
        parts = url.rstrip("/").split("/")
        name = parts[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name

    def clone(self) -> bool:
        """Clone the repository. Returns True on success."""
        try:
            subprocess.run(
                ["git", "clone", self.url, str(self.path)],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to clone {self.url}: {e.stderr}") from e

    def setup_review(self) -> bool:
        """Setup git-review for Gerrit. Returns True on success."""
        try:
            subprocess.run(
                ["git", "review", "-s"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to setup git-review: {e.stderr}") from e

    def has_changes(self) -> bool:
        """Check if repository has uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to check status: {e.stderr}") from e

    def stage_all(self) -> bool:
        """Stage all changes. Returns True on success."""
        try:
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to stage changes: {e.stderr}") from e

    def commit(self, message: str) -> str:
        """Create a commit with the given message (signed-off). Returns commit hash."""
        try:
            subprocess.run(
                ["git", "commit", "-s", "-m", message],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Get the commit hash
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to commit: {e.stderr}") from e

    def submit_review(self, topic: str | None = None) -> bool:
        """Submit changes for review using git-review."""
        try:
            cmd = ["git", "review"]
            if topic:
                cmd.extend(["-t", topic])

            subprocess.run(
                cmd, cwd=self.path, capture_output=True, text=True, check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to submit for review: {e.stderr}") from e

    def run_command(self, command: str) -> tuple[bool, str, str]:
        """
        Run a shell command in the repository directory.
        Returns (success, stdout, stderr).
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.path,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "", "Command timed out after 10 minutes")
        except Exception as e:
            return (False, "", str(e))

    def get_current_branch(self) -> str:
        """Get the current branch name. Returns empty string if in detached HEAD."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            branch = result.stdout.strip()
            # "HEAD" means detached HEAD state
            return "" if branch == "HEAD" else branch
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to get current branch: {e.stderr}") from e

    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally or remotely (on origin)."""
        try:
            # Check local branches
            result = subprocess.run(
                ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"],
                cwd=self.path,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return True

            # Check remote branches on origin
            result = subprocess.run(
                ["git", "show-ref", "--verify", f"refs/remotes/origin/{branch_name}"],
                cwd=self.path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception as e:
            raise RepositoryError(f"Failed to check branch existence: {e}") from e

    def branch_exists_locally(self, branch_name: str) -> bool:
        """Check if a branch exists locally."""
        try:
            result = subprocess.run(
                ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"],
                cwd=self.path,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception as e:
            raise RepositoryError(f"Failed to check local branch existence: {e}") from e

    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch. Returns True on success."""
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to create branch: {e.stderr}") from e

    def checkout_branch(self, branch_name: str) -> bool:
        """
        Switch to an existing branch. Returns True on success.

        If the branch exists locally, checks it out directly.
        If it only exists remotely (on origin), creates a local tracking branch.
        """
        try:
            # Check if branch exists locally
            if self.branch_exists_locally(branch_name):
                # Branch exists locally, just check it out
                subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=self.path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                # Branch doesn't exist locally, create tracking branch from origin
                # This avoids ambiguity when the branch exists in multiple remotes
                subprocess.run(
                    ["git", "checkout", "-b", branch_name, f"origin/{branch_name}"],
                    cwd=self.path,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            return True
        except subprocess.CalledProcessError as e:
            raise RepositoryError(f"Failed to checkout branch: {e.stderr}") from e

    def has_uncommitted_changes(self) -> bool:
        """
        Check if repository has uncommitted changes (both staged and unstaged).
        This is the same as has_changes() but with a more descriptive name.
        """
        return self.has_changes()
