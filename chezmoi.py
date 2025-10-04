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
    def get_status(cls) -> str:
        """Get chezmoi status.

        Returns:
            str: Status output similar to git status.
        """
        result = cls.run_command(["status"])
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
    def apply(cls, dry_run: bool = False, verbose: bool = True) -> str:
        """Apply changes.

        Args:
            dry_run: Preview changes without applying.
            verbose: Verbose output.

        Returns:
            str: Apply output.
        """
        args = ["apply"]
        if verbose:
            args.append("--verbose")
        if dry_run:
            args.append("--dry-run")
        result = cls.run_command(args)
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
