"""
Tests for workspace module.
"""

from pathlib import Path

import pytest

from roller.workspace import Workspace


class TestWorkspace:
    """Tests for Workspace class."""

    def test_create_workspace(self, temp_dir: Path):
        """Test creating a workspace."""
        workspace = Workspace(base_dir=temp_dir)
        path = workspace.create()

        assert path.exists()
        assert path.is_dir()
        assert path.parent == temp_dir
        assert path.name.startswith("changes-roller-")
        assert workspace.path == path

    def test_create_workspace_default_dir(self):
        """Test creating a workspace with default directory."""
        workspace = Workspace()
        path = workspace.create()

        assert path.exists()
        assert path.is_dir()
        assert path.name.startswith("changes-roller-")

        # Clean up
        workspace.cleanup()
        assert not path.exists()

    def test_create_multiple_workspaces_unique(self, temp_dir: Path):
        """Test that multiple workspaces have unique IDs."""
        workspace1 = Workspace(base_dir=temp_dir)
        workspace2 = Workspace(base_dir=temp_dir)

        path1 = workspace1.create()
        path2 = workspace2.create()

        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

    def test_get_repo_path(self, temp_dir: Path):
        """Test getting repository path within workspace."""
        workspace = Workspace(base_dir=temp_dir)
        workspace.create()

        repo_path = workspace.get_repo_path("test-repo")

        assert repo_path == workspace.path / "test-repo"
        assert repo_path.parent == workspace.path

    def test_get_repo_path_before_create(self, temp_dir: Path):
        """Test getting repository path before workspace is created."""
        workspace = Workspace(base_dir=temp_dir)

        with pytest.raises(RuntimeError, match="Workspace not created yet"):
            workspace.get_repo_path("test-repo")

    def test_cleanup_workspace(self, temp_dir: Path):
        """Test cleaning up workspace."""
        workspace = Workspace(base_dir=temp_dir)
        path = workspace.create()

        # Create some files in the workspace
        test_file = path / "test.txt"
        test_file.write_text("test content")
        test_dir = path / "subdir"
        test_dir.mkdir()

        assert path.exists()
        assert test_file.exists()
        assert test_dir.exists()

        workspace.cleanup()

        assert not path.exists()
        assert not test_file.exists()
        assert not test_dir.exists()
        assert workspace.path is None

    def test_cleanup_nonexistent_workspace(self, temp_dir: Path):
        """Test cleanup when workspace doesn't exist."""
        workspace = Workspace(base_dir=temp_dir)
        # Don't call create()

        # Should not raise an error
        workspace.cleanup()
        assert workspace.path is None

    def test_cleanup_already_deleted_workspace(self, temp_dir: Path):
        """Test cleanup when workspace was already deleted."""
        workspace = Workspace(base_dir=temp_dir)
        path = workspace.create()

        # Manually delete the workspace
        import shutil

        shutil.rmtree(path)

        # Cleanup should not raise an error
        workspace.cleanup()
        assert workspace.path is None

    def test_workspace_path_structure(self, temp_dir: Path):
        """Test that workspace path follows expected structure."""
        workspace = Workspace(base_dir=temp_dir)
        path = workspace.create()

        # Check the workspace ID is a valid hex token (12 chars)
        workspace_id = path.name.replace("changes-roller-", "")
        assert len(workspace_id) == 12
        # All characters should be valid hex
        int(workspace_id, 16)  # This will raise if not valid hex
