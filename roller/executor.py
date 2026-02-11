"""
Main executor for coordinating patch series operations.
"""

import concurrent.futures
from pathlib import Path

from .config import SeriesConfig
from .reporter import Reporter, Status
from .repository import Repository, RepositoryError
from .workspace import Workspace


class PatchExecutor:
    """Orchestrates patch series execution across multiple repositories."""

    def __init__(
        self, config: SeriesConfig, reporter: Reporter, exit_on_error: bool = False
    ):
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
                    self._process_repository, url, idx + 1, total, script_path
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

    def _process_repository(
        self, url: str, index: int, total: int, script_path: Path
    ) -> bool:
        """Process a single repository. Returns True on success."""
        assert self.workspace.path is not None, "Workspace must be created first"
        repo = Repository(url, self.workspace.path)

        self.reporter.print_repo_start(index, total, repo.name)

        original_branch: str | None = None

        try:
            # Clone repository
            if self.config.dry_run:
                self.reporter.print_step(Status.INFO, "[DRY RUN] Would clone repository")
            else:
                repo.clone()
                self.reporter.print_step(Status.SUCCESS, "Cloned repository")

            # Setup git-review for Gerrit
            if not self.config.dry_run:
                repo.setup_review()
                self.reporter.print_step(Status.SUCCESS, "Setup git-review")

            # Handle branch switching
            if self.config.branch:
                if self.config.dry_run:
                    self.reporter.print_step(
                        Status.INFO, f"[DRY RUN] Would switch to branch '{self.config.branch}'"
                    )
                else:
                    original_branch = repo.get_current_branch()
                    if original_branch:
                        self.reporter.print_step(
                            Status.INFO, f"Current branch: {original_branch}"
                        )

                    # Check for uncommitted changes
                    if repo.has_uncommitted_changes():
                        raise RepositoryError(
                            "Repository has uncommitted changes. "
                            "Please commit or stash them before switching branches."
                        )

                    # Check if target branch exists
                    if repo.branch_exists(self.config.branch):
                        repo.checkout_branch(self.config.branch)
                        self.reporter.print_step(
                            Status.SUCCESS, f"Switched to branch '{self.config.branch}'"
                        )
                    elif self.config.create_branch:
                        repo.create_branch(self.config.branch)
                        self.reporter.print_step(
                            Status.SUCCESS, f"Created and switched to branch '{self.config.branch}'"
                        )
                    else:
                        raise RepositoryError(
                            f"Branch '{self.config.branch}' does not exist. "
                            "Use --create-branch to create it."
                        )

            # Execute pre-commands
            if self.config.pre_commands:
                for cmd in self.config.pre_commands:
                    if self.config.dry_run:
                        self.reporter.print_step(
                            Status.INFO, f"[DRY RUN] Would run pre-command: {cmd}"
                        )
                    else:
                        if not self._execute_command(repo, cmd, "pre-command"):
                            if not self.config.continue_on_error:
                                self.reporter.add_result(
                                    repo.name, "failed", f"Pre-command failed: {cmd}"
                                )
                                return False

            # Execute patch script
            if self.config.dry_run:
                self.reporter.print_step(
                    Status.INFO, f"[DRY RUN] Would execute patch script: {script_path}"
                )
            else:
                success, _stdout, stderr = repo.run_command(str(script_path.absolute()))
                if not success:
                    self.reporter.print_step(
                        Status.FAILED, "Patch script failed (exit code non-zero)"
                    )
                    if stderr:
                        self.reporter.print_step(
                            Status.INFO, f"Error: {stderr.strip()}", indent=4
                        )
                    self.reporter.add_result(repo.name, "failed", "Patch script failed")
                    return False

                self.reporter.print_step(Status.SUCCESS, "Executed patch script")

            # Check for changes
            if not self.config.dry_run:
                if not repo.has_changes():
                    self.reporter.print_step(Status.INFO, "No changes detected, skipping")
                    self.reporter.add_result(repo.name, "skipped", "No changes")
                    return True

            # Run tests if configured
            if self.config.run_tests:
                if self.config.dry_run:
                    self.reporter.print_step(
                        Status.INFO, f"[DRY RUN] Would run tests: {self.config.test_command}"
                    )
                else:
                    self.reporter.print_step(
                        Status.RUNNING, f"Running tests ({self.config.test_command})..."
                    )
                    test_success, _test_stdout, _test_stderr = repo.run_command(
                        self.config.test_command
                    )

                    if test_success:
                        self.reporter.print_step(Status.SUCCESS, "Tests PASSED")
                    else:
                        self.reporter.print_step(Status.FAILED, "Tests FAILED")
                        if self.config.tests_blocking:
                            self.reporter.add_result(
                                repo.name, "failed", "Tests failed (blocking)"
                            )
                            return False
                        else:
                            self.reporter.print_step(
                                Status.INFO,
                                "Continuing despite test failure (non-blocking)",
                                indent=4,
                            )

            # Commit changes if enabled
            if self.config.commit:
                if self.config.dry_run:
                    self.reporter.print_step(
                        Status.INFO, "[DRY RUN] Would commit changes"
                    )
                else:
                    repo.stage_all()
                    commit_msg = self._render_commit_message(repo.name)
                    commit_hash = repo.commit(commit_msg)
                    self.reporter.print_step(
                        Status.SUCCESS, f"Committed changes ({commit_hash})"
                    )

                # Submit for review if enabled
                if self.config.review:
                    if self.config.dry_run:
                        self.reporter.print_step(
                            Status.INFO, "[DRY RUN] Would submit for review"
                        )
                    else:
                        topic = self.config.topic if self.config.topic else None
                        repo.submit_review(topic)
                        self.reporter.print_step(Status.SUCCESS, "Submitted for review")

            # Execute post-commands
            if self.config.post_commands:
                for cmd in self.config.post_commands:
                    if self.config.dry_run:
                        self.reporter.print_step(
                            Status.INFO, f"[DRY RUN] Would run post-command: {cmd}"
                        )
                    else:
                        if not self._execute_command(repo, cmd, "post-command"):
                            if not self.config.continue_on_error:
                                self.reporter.add_result(
                                    repo.name, "failed", f"Post-command failed: {cmd}"
                                )
                                return False

            # Return to original branch if needed
            if (
                self.config.branch
                and original_branch
                and not self.config.stay_on_branch
            ):
                if self.config.dry_run:
                    self.reporter.print_step(
                        Status.INFO, f"[DRY RUN] Would return to branch '{original_branch}'"
                    )
                else:
                    repo.checkout_branch(original_branch)
                    self.reporter.print_step(
                        Status.SUCCESS, f"Returned to branch '{original_branch}'"
                    )

            self.reporter.add_result(repo.name, "succeeded")
            return True

        except RepositoryError as e:
            self.reporter.print_step(Status.FAILED, str(e))
            self.reporter.add_result(repo.name, "failed", str(e))
            return False
        except Exception as e:
            self.reporter.print_step(Status.FAILED, f"Unexpected error: {e}")
            self.reporter.add_result(repo.name, "failed", str(e))
            return False

    def _render_commit_message(self, repo_name: str) -> str:
        """Render commit message template with variables."""
        message = self.config.commit_msg
        # Replace template variables
        message = message.replace("{{ project_name }}", repo_name)
        message = message.replace("{{project_name}}", repo_name)
        return message

    def _execute_command(
        self, repo: Repository, command: str, command_type: str
    ) -> bool:
        """
        Execute a command and report results.
        Returns True on success, False on failure.
        """
        self.reporter.print_step(Status.RUNNING, f"Running {command_type}: {command}")
        success, stdout, stderr = repo.run_command(command)

        if success:
            self.reporter.print_step(Status.SUCCESS, f"{command_type.capitalize()} succeeded")
            if stdout.strip():
                for line in stdout.strip().split("\n")[:10]:  # Show first 10 lines
                    self.reporter.print_step(Status.INFO, line, indent=4)
        else:
            self.reporter.print_step(Status.FAILED, f"{command_type.capitalize()} failed")
            if stderr.strip():
                for line in stderr.strip().split("\n")[:10]:  # Show first 10 lines
                    self.reporter.print_step(Status.INFO, f"Error: {line}", indent=4)
            if self.config.continue_on_error:
                self.reporter.print_step(
                    Status.INFO,
                    "Continuing despite command failure (--continue-on-error)",
                    indent=4,
                )

        return success
