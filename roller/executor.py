"""
Main executor for coordinating patch series operations.
"""

import concurrent.futures
from pathlib import Path
from typing import List

from .config import SeriesConfig
from .workspace import Workspace
from .repository import Repository, RepositoryError
from .reporter import Reporter, Status


class PatchExecutor:
    """Orchestrates patch series execution across multiple repositories."""

    def __init__(self, config: SeriesConfig, reporter: Reporter, exit_on_error: bool = False):
        self.config = config
        self.reporter = reporter
        self.exit_on_error = exit_on_error
        self.workspace = Workspace()

    def execute(self) -> bool:
        """
        Execute the patch series across all repositories.
        Returns True if all operations succeeded.
        """
        # Create workspace
        workspace_path = self.workspace.create()
        self.reporter.print_header(self.config.topic, str(workspace_path))

        # Validate patch script exists
        script_path = Path(self.config.commands)
        if not script_path.exists():
            print(f"Error: Patch script not found: {script_path}")
            return False

        if not script_path.is_file():
            print(f"Error: Patch script is not a file: {script_path}")
            return False

        # Make script executable
        script_path.chmod(0o755)

        # Process repositories in parallel
        total = len(self.config.projects)
        all_success = True

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self._process_repository,
                    url,
                    idx + 1,
                    total,
                    script_path
                ): url
                for idx, url in enumerate(self.config.projects)
            }

            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    success = future.result()
                    if not success:
                        all_success = False
                        if self.exit_on_error:
                            print("\nExiting due to error (--exit-on-error flag)")
                            # Cancel remaining futures
                            for f in futures:
                                f.cancel()
                            break
                except Exception as e:
                    print(f"\nUnexpected error processing {url}: {e}")
                    all_success = False
                    if self.exit_on_error:
                        break

        # Print summary
        self.reporter.print_summary()

        return all_success

    def _process_repository(self, url: str, index: int, total: int, script_path: Path) -> bool:
        """Process a single repository. Returns True on success."""
        repo = Repository(url, self.workspace.path)

        self.reporter.print_repo_start(index, total, repo.name)

        try:
            # Clone repository
            repo.clone()
            self.reporter.print_step(Status.SUCCESS, "Cloned repository")

            # Setup git-review for Gerrit
            repo.setup_review()
            self.reporter.print_step(Status.SUCCESS, "Setup git-review")

            # Execute patch script
            success, stdout, stderr = repo.run_command(str(script_path.absolute()))
            if not success:
                self.reporter.print_step(
                    Status.FAILED,
                    f"Patch script failed (exit code non-zero)"
                )
                if stderr:
                    self.reporter.print_step(Status.INFO, f"Error: {stderr.strip()}", indent=4)
                self.reporter.add_result(repo.name, 'failed', 'Patch script failed')
                return False

            self.reporter.print_step(Status.SUCCESS, "Executed patch script")

            # Check for changes
            if not repo.has_changes():
                self.reporter.print_step(Status.INFO, "No changes detected, skipping")
                self.reporter.add_result(repo.name, 'skipped', 'No changes')
                return True

            # Run tests if configured
            if self.config.run_tests:
                self.reporter.print_step(Status.RUNNING, f"Running tests ({self.config.test_command})...")
                test_success, test_stdout, test_stderr = repo.run_command(self.config.test_command)

                if test_success:
                    self.reporter.print_step(Status.SUCCESS, "Tests PASSED")
                else:
                    self.reporter.print_step(Status.FAILED, "Tests FAILED")
                    if self.config.tests_blocking:
                        self.reporter.add_result(repo.name, 'failed', 'Tests failed (blocking)')
                        return False
                    else:
                        self.reporter.print_step(Status.INFO, "Continuing despite test failure (non-blocking)", indent=4)

            # Commit changes if enabled
            if self.config.commit:
                repo.stage_all()
                commit_msg = self._render_commit_message(repo.name)
                commit_hash = repo.commit(commit_msg)
                self.reporter.print_step(Status.SUCCESS, f"Committed changes ({commit_hash})")

                # Submit for review if enabled
                if self.config.review:
                    topic = self.config.topic if self.config.topic else None
                    repo.submit_review(topic)
                    self.reporter.print_step(Status.SUCCESS, "Submitted for review")

            self.reporter.add_result(repo.name, 'succeeded')
            return True

        except RepositoryError as e:
            self.reporter.print_step(Status.FAILED, str(e))
            self.reporter.add_result(repo.name, 'failed', str(e))
            return False
        except Exception as e:
            self.reporter.print_step(Status.FAILED, f"Unexpected error: {e}")
            self.reporter.add_result(repo.name, 'failed', str(e))
            return False

    def _render_commit_message(self, repo_name: str) -> str:
        """Render commit message template with variables."""
        message = self.config.commit_msg
        # Replace template variables
        message = message.replace('{{ project_name }}', repo_name)
        message = message.replace('{{project_name}}', repo_name)
        return message
