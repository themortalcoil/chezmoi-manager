"""Custom widgets for the application."""

from textual.widgets import Input, Static, Label
from textual.containers import Container, Vertical
from textual import on
from pathlib import Path


class FileInput(Input):
    """Input widget for file paths with validation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = "Enter file path (e.g., ~/.bashrc)"
    
    def validate_path(self, path: str) -> tuple[bool, str]:
        """Validate a file path.
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path or not path.strip():
            return False, "Path cannot be empty"
        
        try:
            expanded_path = Path(path).expanduser()
            if not expanded_path.exists():
                return False, "File does not exist"
            if not expanded_path.is_file():
                return False, "Path is not a file"
            return True, ""
        except Exception as e:
            return False, f"Invalid path: {str(e)}"


class ResultPanel(Static):
    """Panel for displaying operation results."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Result"
    
    def show_success(self, message: str) -> None:
        """Display a success message.
        
        Args:
            message: Success message to display
        """
        self.update(f"[green]✓ {message}[/green]")
    
    def show_error(self, message: str) -> None:
        """Display an error message.
        
        Args:
            message: Error message to display
        """
        self.update(f"[red]✗ {message}[/red]")
    
    def show_info(self, message: str) -> None:
        """Display an info message.
        
        Args:
            message: Info message to display
        """
        self.update(f"[blue]ℹ {message}[/blue]")
    
    def clear(self) -> None:
        """Clear the result panel."""
        self.update("")


class OptionsPanel(Container):
    """Panel for chezmoi file options."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Options"
    
    def compose(self):
        """Compose the options panel."""
        from textual.widgets import Checkbox
        
        yield Checkbox("Template", id="template_check")
        yield Checkbox("Encrypt", id="encrypt_check")
        yield Checkbox("Private", id="private_check")
        yield Checkbox("Executable", id="executable_check")
        yield Checkbox("Readonly", id="readonly_check")
        yield Checkbox("Exact", id="exact_check")
    
    def get_options(self) -> dict[str, bool]:
        """Get the current option values.
        
        Returns:
            Dictionary of option names to boolean values
        """
        return {
            "template": self.query_one("#template_check").value,
            "encrypt": self.query_one("#encrypt_check").value,
            "private": self.query_one("#private_check").value,
            "executable": self.query_one("#executable_check").value,
            "readonly": self.query_one("#readonly_check").value,
            "exact": self.query_one("#exact_check").value,
        }
    
    def reset(self) -> None:
        """Reset all options to unchecked."""
        for checkbox in self.query("Checkbox"):
            checkbox.value = False


class PreviewPanel(Static):
    """Panel for previewing changes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Preview"
    
    def update_preview(self, path: str, options: dict[str, bool]) -> None:
        """Update the preview with current settings.
        
        Args:
            path: File path
            options: Dictionary of options
        """
        if not path:
            self.update("[dim]Enter a file path to see preview[/dim]")
            return
        
        lines = [f"[bold]File:[/bold] {path}"]
        
        enabled_options = [k for k, v in options.items() if v]
        if enabled_options:
            lines.append(f"[bold]Options:[/bold] {', '.join(enabled_options)}")
        else:
            lines.append("[dim]No options enabled[/dim]")
        
        if options.get("template"):
            lines.append("[yellow]💡 Remember to use {{ .variable }} syntax in templates[/yellow]")
        
        if options.get("encrypt"):
            lines.append("[yellow]🔐 File will be encrypted with age[/yellow]")
        
        if options.get("exact"):
            lines.append("[yellow]⚠️  Exact mode: file permissions will be preserved exactly[/yellow]")
        
        self.update("\n".join(lines))
