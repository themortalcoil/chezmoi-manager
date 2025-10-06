"""File browser screen for exploring chezmoi source directory."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Static

from chezmoi import ChezmoiWrapper


class FileInfoPanel(Static):
    """Panel showing information about selected file."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("[bold]File Information[/bold]", id="info-title")
        yield Static("[dim]Select a file to view details[/dim]", id="info-content")

    def update_info(self, path: Path) -> None:
        """Update info panel with file details."""
        content = self.query_one("#info-content", Static)

        if path.is_file():
            size = path.stat().st_size
            size_str = self._format_size(size)

            # Get target path
            try:
                target = ChezmoiWrapper.run_command(
                    ["target-path", str(path)]
                ).stdout.strip()
            except Exception:
                target = "Unknown"

            info_text = f"""[cyan]Source:[/cyan] {path.name}
[cyan]Target:[/cyan] {target}
[cyan]Size:[/cyan] {size_str}
[cyan]Type:[/cyan] File"""
        elif path.is_dir():
            try:
                file_count = len(list(path.iterdir()))
            except PermissionError:
                file_count = 0

            info_text = f"""[cyan]Directory:[/cyan] {path.name}
[cyan]Items:[/cyan] {file_count}
[cyan]Type:[/cyan] Directory"""
        else:
            info_text = f"[yellow]Path:[/yellow] {path}"

        content.update(info_text)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FileBrowserScreen(Screen):
    """Screen for browsing chezmoi source directory."""

    CSS = """
    FileBrowserScreen {
        layout: horizontal;
    }

    #file-tree-container {
        width: 60%;
        height: 100%;
        border-right: solid $primary;
    }

    #file-info-container {
        width: 40%;
        height: 100%;
        padding: 1 2;
    }

    DirectoryTree {
        height: 1fr;
    }

    #info-title {
        padding: 1 0;
        text-style: bold;
    }

    #info-content {
        padding: 1 0;
    }

    #actions-container {
        dock: bottom;
        height: auto;
        width: 100%;
        background: $panel;
        border-top: solid $primary;
        padding: 1 2;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("r", "refresh", "Refresh"),
        ("d", "show_diff", "Show Diff"),
        ("q", "app.quit", "Quit"),
    ]

    def __init__(self) -> None:
        """Initialize the screen."""
        super().__init__()
        try:
            self.source_dir = ChezmoiWrapper.get_source_dir()
        except Exception:
            self.source_dir = Path.home() / ".local" / "share" / "chezmoi"

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Horizontal():
            with Vertical(id="file-tree-container"):
                yield DirectoryTree(str(self.source_dir))

            with Vertical(id="file-info-container"):
                yield FileInfoPanel()

        with Horizontal(id="actions-container"):
            yield Button("Show Diff", variant="primary", id="btn-diff")
            yield Button("Refresh", variant="success", id="btn-refresh")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.title = "File Browser"
        self.sub_title = f"Browsing: {self.source_dir}"

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection."""
        info_panel = self.query_one(FileInfoPanel)
        info_panel.update_info(event.path)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """Handle directory selection."""
        info_panel = self.query_one(FileInfoPanel)
        info_panel.update_info(event.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-diff":
            self.action_show_diff()

    def action_refresh(self) -> None:
        """Refresh the directory tree."""
        tree = self.query_one(DirectoryTree)
        tree.reload()
        self.app.notify("Directory tree refreshed", timeout=1)

    def action_show_diff(self) -> None:
        """Show diff for selected file."""
        # TODO: Get selected file and show diff
        self.app.notify("Diff viewer coming soon!", title="Info")

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
