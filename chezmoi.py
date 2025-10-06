"""Wrapper for chezmoi CLI operations."""

import json
import subprocess
from pathlib import Path
from typing import Any


class ChezmoiError(Exception):
    """Base exception for chezmoi wrapper errors."""

    pass


class ChezmoiNotFoundError(ChezmoiError):
    """Raised when chezmoi is not installed."""

    pass


class ChezmoiCommandError(ChezmoiError):
    """Raised when a chezmoi command fails."""

    def __init__(self, message: str, stderr: str = "", returncode: int = 1):
        """Initialize with error details.

        Args:
            message: Error message.
            stderr: Standard error output.
            returncode: Command return code.
        """
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


class ChezmoiWrapper:
    """Wrapper for chezmoi CLI operations.

    This class provides a Python interface to the chezmoi command-line tool,
    handling subprocess execution and result parsing.
    """

    @staticmethod
    def check_installed() -> bool:
        """Check if chezmoi is installed and available.

        Returns:
            bool: True if chezmoi is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["chezmoi", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def get_version() -> str:
        """Get chezmoi version.

        Returns:
            str: Version string.

        Raises:
            ChezmoiNotFoundError: If chezmoi is not installed.
        """
        try:
            result = subprocess.run(
                ["chezmoi", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except FileNotFoundError:
            raise ChezmoiNotFoundError("chezmoi is not installed or not in PATH")

    @staticmethod
    def run_command(
        args: list[str],
        format: str | None = None,
        check: bool = False,
        timeout: int = 30,
    ) -> subprocess.CompletedProcess:
        """Run a chezmoi command.

        Args:
            args: Command arguments (without 'chezmoi' prefix).
            format: Output format (json, yaml, or None).
            check: Raise exception on non-zero exit code.
            timeout: Command timeout in seconds.

        Returns:
            subprocess.CompletedProcess: Command result.

        Raises:
            ChezmoiNotFoundError: If chezmoi is not installed.
            subprocess.CalledProcessError: If check=True and command fails.
        """
        cmd = ["chezmoi"] + args
        if format:
            cmd += ["--format", format]

        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                timeout=timeout,
            )
        except FileNotFoundError:
            raise ChezmoiNotFoundError("chezmoi is not installed or not in PATH")

    @classmethod
    def get_status(cls, targets: list[str] | None = None) -> str:
        """Get chezmoi status.

        Args:
            targets: Optional list of specific targets to check status for.

        Returns:
            str: Status output similar to git status.
        """
        args = ["status"]
        if targets:
            args.extend(targets)
        result = cls.run_command(args)
        return result.stdout

    @classmethod
    def get_managed_files(cls) -> list[str]:
        """Get list of managed files.

        Returns:
            list[str]: List of managed file paths.
        """
        result = cls.run_command(["managed"])
        if result.returncode == 0 and result.stdout.strip():
            # Parse line-by-line output
            return [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
        return []

    @classmethod
    def get_diff(cls, target: str = "") -> str:
        """Get diff for target or all files.

        Args:
            target: Specific target file (empty for all files).

        Returns:
            str: Diff output.
        """
        args = ["diff"]
        if target:
            args.append(target)
        result = cls.run_command(args)
        return result.stdout

    @classmethod
    def apply(
        cls,
        targets: list[str] | None = None,
        dry_run: bool = False,
        verbose: bool = True,
    ) -> str:
        """Apply changes.

        Args:
            targets: Optional list of specific targets to apply.
            dry_run: Preview changes without applying.
            verbose: Verbose output.

        Returns:
            str: Apply output.

        Raises:
            ChezmoiCommandError: If apply fails.
        """
        args = ["apply"]
        if verbose:
            args.append("--verbose")
        if dry_run:
            args.append("--dry-run")
        if targets:
            args.extend(targets)

        result = cls.run_command(args)

        if result.returncode != 0:
            raise ChezmoiCommandError(
                "Failed to apply changes",
                stderr=result.stderr,
                returncode=result.returncode,
            )

        return result.stdout

    @classmethod
    def get_data(cls) -> dict[str, Any]:
        """Get template data.

        Returns:
            dict: Template data as dictionary.
        """
        result = cls.run_command(["data", "--format", "json"])
        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {}
        return {}

    @classmethod
    def get_source_path(cls, target: str = "") -> str:
        """Get source directory path or source path of a target.

        Args:
            target: Target file (empty for source directory).

        Returns:
            str: Source path.
        """
        args = ["source-path"]
        if target:
            args.append(target)
        result = cls.run_command(args)
        return result.stdout.strip()

    @classmethod
    def get_source_dir(cls) -> Path:
        """Get source directory as Path object.

        Returns:
            Path: Source directory path.
        """
        return Path(cls.get_source_path())

    @classmethod
    def doctor(cls) -> str:
        """Run chezmoi doctor to check for problems.

        Returns:
            str: Doctor output.
        """
        result = cls.run_command(["doctor"])
        return result.stdout

    @classmethod
    def verify(cls) -> tuple[bool, str]:
        """Verify the source state is in a consistent state.

        Returns:
            tuple[bool, str]: (success, output) - True if verification passed.
        """
        result = cls.run_command(["verify"])
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        return (success, output.strip())

    @classmethod
    def add(
        cls,
        targets: list[str] | str,
        template: bool = False,
        encrypt: bool = False,
        recursive: bool = True,
        exact: bool = False,
        autotemplate: bool = False,
        follow: bool = False,
        create: bool = False,
        prompt: bool = False,
    ) -> str:
        """Add files to the source state.

        Args:
            targets: File path(s) to add.
            template: Set template attribute on added files.
            encrypt: Encrypt files using defined encryption method.
            recursive: Recurse into subdirectories (default: True).
            exact: Set exact attribute on added directories.
            autotemplate: Automatically generate templates.
            follow: Add symlink target instead of symlink itself.
            create: Add files that should exist, regardless of contents.
            prompt: Interactively prompt before adding each file.

        Returns:
            str: Command output.

        Raises:
            ChezmoiCommandError: If the add command fails.
        """
        if isinstance(targets, str):
            targets = [targets]

        args = ["add"]

        # Add flags
        if template:
            args.append("--template")
        if encrypt:
            args.append("--encrypt")
        if not recursive:
            args.append("--recursive=false")
        if exact:
            args.append("--exact")
        if autotemplate:
            args.append("--autotemplate")
        if follow:
            args.append("--follow")
        if create:
            args.append("--create")
        if prompt:
            args.append("--prompt")

        args.extend(targets)
        result = cls.run_command(args)

        if result.returncode != 0:
            raise ChezmoiCommandError(
                f"Failed to add files: {targets}",
                stderr=result.stderr,
                returncode=result.returncode,
            )

        return result.stdout

    @classmethod
    def remove(cls, targets: list[str] | str) -> str:
        """Remove files from the source state.

        Args:
            targets: File path(s) to remove.

        Returns:
            str: Command output.

        Raises:
            ChezmoiCommandError: If the remove command fails.
        """
        if isinstance(targets, str):
            targets = [targets]

        args = ["remove"] + targets
        result = cls.run_command(args)

        if result.returncode != 0:
            raise ChezmoiCommandError(
                f"Failed to remove files: {targets}",
                stderr=result.stderr,
                returncode=result.returncode,
            )

        return result.stdout

    @classmethod
    def edit(cls, target: str) -> str:
        """Get the command to edit a file in the source state.

        Args:
            target: File path to edit.

        Returns:
            str: Editor command or source path.
        """
        result = cls.run_command(["source-path", target])
        return result.stdout.strip()

    @classmethod
    def update(cls, apply: bool = True) -> str:
        """Pull changes from the remote repository and optionally apply.

        Args:
            apply: Whether to apply changes after updating.

        Returns:
            str: Command output.
        """
        args = ["update"]
        if not apply:
            args.append("--no-apply")

        result = cls.run_command(args)
        return result.stdout

    @classmethod
    def get_target_path(cls, source: str) -> str:
        """Get the target path for a source file.

        Args:
            source: Source file path.

        Returns:
            str: Target path.
        """
        # Remove source directory prefix and decode chezmoi naming
        # This is a simplified version - full implementation would decode
        # all chezmoi naming conventions (dot_, private_, etc.)
        source_dir = cls.get_source_dir()
        rel_path = Path(source).relative_to(source_dir)

        # Basic decoding
        target = str(rel_path)
        if target.startswith("dot_"):
            target = "." + target[4:]

        return target

    @classmethod
    def init(cls, repo: str = "") -> str:
        """Initialize chezmoi with optional git repository.

        Args:
            repo: Git repository URL (optional).

        Returns:
            str: Command output.

        Raises:
            ChezmoiCommandError: If initialization fails.
        """
        args = ["init"]
        if repo:
            args.append(repo)

        result = cls.run_command(args)

        if result.returncode != 0:
            raise ChezmoiCommandError(
                f"Failed to initialize chezmoi{f' with repo {repo}' if repo else ''}",
                stderr=result.stderr,
                returncode=result.returncode,
            )

        return result.stdout
