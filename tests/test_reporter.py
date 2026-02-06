"""
Tests for reporter module.
"""

import pytest

from roller.reporter import Reporter, Status


class TestStatus:
    """Tests for Status enum."""

    def test_status_values(self):
        """Test that status enum has expected values."""
        assert Status.SUCCESS.value == "✓"
        assert Status.FAILED.value == "✗"
        assert Status.INFO.value == "ℹ"
        assert Status.RUNNING.value == "→"


class TestReporter:
    """Tests for Reporter class."""

    def test_reporter_creation(self):
        """Test creating a Reporter instance."""
        reporter = Reporter(verbose=False)
        assert reporter.verbose is False
        assert reporter.results == []

    def test_reporter_verbose_mode(self):
        """Test creating a Reporter with verbose mode."""
        reporter = Reporter(verbose=True)
        assert reporter.verbose is True

    def test_print_header(self, capsys):
        """Test printing the series header."""
        reporter = Reporter()
        reporter.print_header("test-topic", "/tmp/workspace")

        captured = capsys.readouterr()
        assert "Starting patch series: test-topic" in captured.out
        assert "Workspace: /tmp/workspace" in captured.out

    def test_print_header_unnamed(self, capsys):
        """Test printing header with no topic."""
        reporter = Reporter()
        reporter.print_header("", "/tmp/workspace")

        captured = capsys.readouterr()
        assert "Starting patch series: unnamed" in captured.out

    def test_print_repo_start(self, capsys):
        """Test printing repository start message."""
        reporter = Reporter()
        reporter.print_repo_start(1, 5, "test-repo")

        captured = capsys.readouterr()
        assert "[1/5]" in captured.out
        assert "Processing test-repo" in captured.out

    def test_print_step_success(self, capsys):
        """Test printing a success step."""
        reporter = Reporter()
        reporter.print_step(Status.SUCCESS, "Operation completed")

        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "Operation completed" in captured.out

    def test_print_step_failed(self, capsys):
        """Test printing a failed step."""
        reporter = Reporter()
        reporter.print_step(Status.FAILED, "Operation failed")

        captured = capsys.readouterr()
        assert "✗" in captured.out
        assert "Operation failed" in captured.out

    def test_print_step_info(self, capsys):
        """Test printing an info step."""
        reporter = Reporter()
        reporter.print_step(Status.INFO, "Additional information")

        captured = capsys.readouterr()
        assert "ℹ" in captured.out
        assert "Additional information" in captured.out

    def test_print_step_running(self, capsys):
        """Test printing a running step."""
        reporter = Reporter()
        reporter.print_step(Status.RUNNING, "Processing...")

        captured = capsys.readouterr()
        assert "→" in captured.out
        assert "Processing..." in captured.out

    def test_print_step_with_indent(self, capsys):
        """Test printing a step with custom indentation."""
        reporter = Reporter()
        reporter.print_step(Status.INFO, "Indented message", indent=4)

        captured = capsys.readouterr()
        # Check for 4 spaces before the status indicator
        assert "    ℹ Indented message" in captured.out

    def test_add_result(self):
        """Test adding a result."""
        reporter = Reporter()
        reporter.add_result("test-repo", "succeeded", "All good")

        assert len(reporter.results) == 1
        assert reporter.results[0]["repo"] == "test-repo"
        assert reporter.results[0]["status"] == "succeeded"
        assert reporter.results[0]["details"] == "All good"

    def test_add_multiple_results(self):
        """Test adding multiple results."""
        reporter = Reporter()
        reporter.add_result("repo1", "succeeded")
        reporter.add_result("repo2", "failed", "Error occurred")
        reporter.add_result("repo3", "skipped", "No changes")

        assert len(reporter.results) == 3
        assert reporter.results[1]["status"] == "failed"
        assert reporter.results[2]["details"] == "No changes"

    def test_print_summary_all_succeeded(self, capsys):
        """Test printing summary with all successes."""
        reporter = Reporter()
        reporter.add_result("repo1", "succeeded")
        reporter.add_result("repo2", "succeeded")

        reporter.print_summary()

        captured = capsys.readouterr()
        assert "Summary:" in captured.out
        assert "Succeeded: 2" in captured.out
        assert "Skipped: 0" in captured.out
        assert "Failed: 0" in captured.out
        assert "Failed repositories:" not in captured.out

    def test_print_summary_mixed_results(self, capsys):
        """Test printing summary with mixed results."""
        reporter = Reporter()
        reporter.add_result("repo1", "succeeded")
        reporter.add_result("repo2", "skipped", "No changes")
        reporter.add_result("repo3", "failed", "Build error")

        reporter.print_summary()

        captured = capsys.readouterr()
        assert "Succeeded: 1" in captured.out
        assert "Skipped: 1" in captured.out
        assert "Failed: 1" in captured.out
        assert "Failed repositories:" in captured.out
        assert "repo3: Build error" in captured.out

    def test_print_summary_multiple_failures(self, capsys):
        """Test printing summary with multiple failures."""
        reporter = Reporter()
        reporter.add_result("repo1", "failed", "Test failure")
        reporter.add_result("repo2", "succeeded")
        reporter.add_result("repo3", "failed", "Compilation error")

        reporter.print_summary()

        captured = capsys.readouterr()
        assert "Failed: 2" in captured.out
        assert "Failed repositories:" in captured.out
        assert "repo1: Test failure" in captured.out
        assert "repo3: Compilation error" in captured.out

    def test_print_summary_empty(self, capsys):
        """Test printing summary with no results."""
        reporter = Reporter()
        reporter.print_summary()

        captured = capsys.readouterr()
        assert "Summary:" in captured.out
        assert "Succeeded: 0" in captured.out
        assert "Skipped: 0" in captured.out
        assert "Failed: 0" in captured.out
