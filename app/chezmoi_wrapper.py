"""Wrapper for chezmoi CLI operations."""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class ChezmoiCommandError(Exception):
    """Exception raised when a chezmoi command fails."""
    pass


class ChezmoiWrapper:
    """Wrapper class for interacting with chezmoi CLI."""
    
    def __init__(self, chezmoi_path: str = "chezmoi"):
        """Initialize the wrapper.
        
        Args:
            chezmoi_path: Path to the chezmoi executable
        """
        self.chezmoi_path = chezmoi_path
    
    def _run_command(self, *args: str, check: bool = True) -> tuple[str, str, int]:
        """Run a chezmoi command.
        
        Args:
            *args: Command arguments
            check: Whether to raise an exception on non-zero exit code
            
        Returns:
            Tuple of (stdout, stderr, returncode)
            
        Raises:
            ChezmoiCommandError: If the command fails and check is True
        """
        try:
            result = subprocess.run(
                [self.chezmoi_path] + list(args),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if check and result.returncode != 0:
                raise ChezmoiCommandError(
                    f"Command failed: {' '.join(args)}\n"
                    f"Error: {result.stderr}"
                )
            
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as e:
            raise ChezmoiCommandError(f"Command timed out: {' '.join(args)}") from e
        except FileNotFoundError as e:
            raise ChezmoiCommandError(
                f"chezmoi not found at {self.chezmoi_path}. "
                "Please install chezmoi or specify the correct path."
            ) from e
    
    def add(
        self,
        path: str,
        template: bool = False,
        encrypt: bool = False,
        exact: bool = False,
        executable: bool = False,
        private: bool = False,
        readonly: bool = False,
    ) -> str:
        """Add a file to chezmoi.
        
        Args:
            path: Path to the file to add
            template: Mark as template
            encrypt: Encrypt the file
            exact: Use exact mode
            executable: Mark as executable
            private: Mark as private
            readonly: Mark as readonly
            
        Returns:
            Command output
            
        Raises:
            ChezmoiCommandError: If the command fails
        """
        args = ["add"]
        
        if template:
            args.append("--template")
        if encrypt:
            args.append("--encrypt")
        if exact:
            args.append("--exact")
        if executable:
            args.append("--executable")
        if private:
            args.append("--private")
        if readonly:
            args.append("--readonly")
        
        args.append(path)
        
        stdout, _, _ = self._run_command(*args)
        return stdout
    
    def remove(self, path: str) -> str:
        """Remove a file from chezmoi.
        
        Args:
            path: Path to the file to remove
            
        Returns:
            Command output
            
        Raises:
            ChezmoiCommandError: If the command fails
        """
        stdout, _, _ = self._run_command("remove", path)
        return stdout
    
    def diff(self, path: Optional[str] = None) -> str:
        """Show diff between current state and chezmoi.
        
        Args:
            path: Optional specific file to diff
            
        Returns:
            Diff output
            
        Raises:
            ChezmoiCommandError: If the command fails
        """
        args = ["diff"]
        if path:
            args.append(path)
        
        stdout, _, _ = self._run_command(*args, check=False)
        return stdout
    
    def apply(self, path: Optional[str] = None) -> str:
        """Apply chezmoi changes.
        
        Args:
            path: Optional specific file to apply
            
        Returns:
            Command output
            
        Raises:
            ChezmoiCommandError: If the command fails
        """
        args = ["apply"]
        if path:
            args.append(path)
        
        stdout, _, _ = self._run_command(*args)
        return stdout
    
    def managed(self) -> list[str]:
        """Get list of managed files.
        
        Returns:
            List of managed file paths
            
        Raises:
            ChezmoiCommandError: If the command fails
        """
        stdout, _, _ = self._run_command("managed")
        return [line.strip() for line in stdout.splitlines() if line.strip()]
    
    def status(self) -> str:
        """Get chezmoi status.
        
        Returns:
            Status output
            
        Raises:
            ChezmoiCommandError: If the command fails
        """
        stdout, _, _ = self._run_command("status")
        return stdout
    
    def is_managed(self, path: str) -> bool:
        """Check if a file is managed by chezmoi.
        
        Args:
            path: Path to check
            
        Returns:
            True if the file is managed
        """
        try:
            managed_files = self.managed()
            # Normalize the path for comparison
            expanded_path = str(Path(path).expanduser().resolve())
            
            for managed in managed_files:
                # Also normalize managed file paths
                try:
                    managed_expanded = str(Path(managed).expanduser().resolve())
                    if expanded_path == managed_expanded:
                        return True
                except Exception:
                    # If normalization fails, skip this managed file
                    continue
            
            return False
        except ChezmoiCommandError:
            return False
