"""
Output formatting and reporting for changes-roller.
"""

from enum import Enum
from typing import List, Dict, Any


class Status(Enum):
    """Status indicators for operations."""
    SUCCESS = "✓"
    FAILED = "✗"
    INFO = "ℹ"
    RUNNING = "→"


class Reporter:
    """Handles formatted output for the CLI."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []

    def print_header(self, topic: str, workspace: str):
        """Print the series header."""
        print(f"\nStarting patch series: {topic or 'unnamed'}")
        print(f"Workspace: {workspace}\n")

    def print_repo_start(self, index: int, total: int, repo_name: str):
        """Print the start of repository processing."""
        print(f"[{index}/{total}] Processing {repo_name}...")

    def print_step(self, status: Status, message: str, indent: int = 2):
        """Print a step with status indicator."""
        prefix = " " * indent
        print(f"{prefix}{status.value} {message}")

    def add_result(self, repo_name: str, status: str, details: str = ""):
        """Record a result for summary."""
        self.results.append({
            'repo': repo_name,
            'status': status,
            'details': details
        })

    def print_summary(self):
        """Print the final summary."""
        succeeded = sum(1 for r in self.results if r['status'] == 'succeeded')
        skipped = sum(1 for r in self.results if r['status'] == 'skipped')
        failed = sum(1 for r in self.results if r['status'] == 'failed')

        print("\nSummary:")
        print(f"  Succeeded: {succeeded}")
        print(f"  Skipped: {skipped}")
        print(f"  Failed: {failed}")

        if failed > 0:
            print("\nFailed repositories:")
            for result in self.results:
                if result['status'] == 'failed':
                    print(f"  - {result['repo']}: {result['details']}")
