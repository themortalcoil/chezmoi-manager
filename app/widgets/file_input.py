"""File input widget with validation."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Input, Label, Static


class FileInput(Static):
    """Input widget for file paths with validation."""

    file_path = reactive("")
    is_valid = reactive(False)

    def __init__(self, placeholder: str = "Enter file path...", **kwargs):
        """Initialize file input.

        Args:
            placeholder: Placeholder text for input.
            **kwargs: Additional widget arguments.
        """
        super().__init__(**kwargs)
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Horizontal():
            yield Input(
                placeholder=self.placeholder,
                id="file-path-input",
            )
            yield Label("", id="validation-status")

    def on_mount(self) -> None:
        """Set up input focus."""
        self.query_one(Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes and validate path."""
        if event.input.id != "file-path-input":
            return

        path_str = event.value.strip()
        self.file_path = path_str

        # Expand ~ to home directory
        if path_str.startswith("~"):
            path_str = str(Path(path_str).expanduser())

        # Validate path
        if not path_str:
            self.is_valid = False
            self.query_one("#validation-status", Label).update("")
        else:
            path = Path(path_str)
            if path.exists():
                self.is_valid = True
                if path.is_file():
                    self.query_one("#validation-status", Label).update(
                        "[green]✓ File[/green]"
                    )
                elif path.is_dir():
                    self.query_one("#validation-status", Label).update(
                        "[green]✓ Directory[/green]"
                    )
                elif path.is_symlink():
                    self.query_one("#validation-status", Label).update(
                        "[green]✓ Symlink[/green]"
                    )
            else:
                self.is_valid = False
                self.query_one("#validation-status", Label).update(
                    "[red]✗ Not found[/red]"
                )

    def get_path(self) -> str:
        """Get the expanded file path.

        Returns:
            str: Expanded file path.
        """
        path_str = self.file_path.strip()
        if path_str.startswith("~"):
            return str(Path(path_str).expanduser())
        return path_str

    def get_path_obj(self) -> Path:
        """Get the path as a Path object.

        Returns:
            Path: Path object for the file.
        """
        return Path(self.get_path())
