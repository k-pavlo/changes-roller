"""
Workspace management for changes-roller.
"""

import tempfile
import secrets
from pathlib import Path
from typing import Optional


class Workspace:
    """Manages temporary workspace for patch series execution."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(tempfile.gettempdir())
        self.path: Optional[Path] = None

    def create(self) -> Path:
        """Create a new workspace directory."""
        # Generate a unique workspace ID
        workspace_id = f"changes-roller-{secrets.token_hex(6)}"
        self.path = self.base_dir / workspace_id
        self.path.mkdir(parents=True, exist_ok=True)
        return self.path

    def cleanup(self):
        """Clean up the workspace directory."""
        if self.path and self.path.exists():
            import shutil
            shutil.rmtree(self.path)
            self.path = None

    def get_repo_path(self, repo_name: str) -> Path:
        """Get the path for a specific repository within the workspace."""
        if not self.path:
            raise RuntimeError("Workspace not created yet")
        return self.path / repo_name
