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
