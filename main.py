"""Chezmoi Manager - A TUI for managing chezmoi dotfiles."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header, Label, Static

from app.screens.data import TemplateDataScreen
from app.screens.diff import DiffViewerScreen
from app.screens.doctor import DoctorScreen
from app.screens.files import FileBrowserScreen
from app.screens.managed import ManagedFilesScreen
from app.screens.status import StatusScreen
from chezmoi import ChezmoiWrapper


class WelcomeScreen(Static):
    """Welcome screen widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold cyan]Welcome to Chezmoi Manager[/bold cyan]")
        yield Label("")
        yield Label("A Terminal User Interface for managing your dotfiles")
        yield Label("")

        # Check if chezmoi is installed
        if ChezmoiWrapper.check_installed():
            version = ChezmoiWrapper.get_version()
            yield Label(f"[green][/green] chezmoi detected: {version}")
        else:
            yield Label("[red][/red] chezmoi not found - please install it first")
            yield Label("  Visit: https://www.chezmoi.io/install/")


class StatusPanel(Static):
    """Display chezmoi status information."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Quick Status[/bold]")
        yield Label("")

        if not ChezmoiWrapper.check_installed():
            yield Label("[yellow]Install chezmoi to see status[/yellow]")
            return

        try:
            # Get managed files count
            managed = ChezmoiWrapper.get_managed_files()
            yield Label(f"Managed files: [cyan]{len(managed)}[/cyan]")

            # Get source directory
            source_dir = ChezmoiWrapper.get_source_dir()
            yield Label(f"Source directory: [dim]{source_dir}[/dim]")

        except Exception as e:
            yield Label(f"[red]Error: {e}[/red]")


class ChezmoiManager(App):
    """A Textual app for managing chezmoi dotfiles."""

    CSS_PATH = "app/styles/base.tcss"

    CSS = """
    Screen {
        background: $surface;
    }

    WelcomeScreen {
        width: 100%;
        height: auto;
        padding: 2 4;
        background: $panel;
        border: solid $primary;
        margin: 1 2;
    }

    StatusPanel {
        width: 100%;
        height: auto;
        padding: 2 4;
        background: $panel;
        border: solid $accent;
        margin: 1 2;
    }

    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("s", "show_status", "Status"),
        Binding("f", "show_files", "Files"),
        Binding("m", "show_managed", "Managed"),
        Binding("v", "show_diff", "Diff"),
        Binding("t", "show_data", "Template Data"),
        Binding("c", "show_doctor", "Doctor"),
        ("ctrl+c", "quit", "Quit"),
    ]

    TITLE = "Chezmoi Manager"
    SUB_TITLE = "Manage your dotfiles with ease"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield WelcomeScreen()
        yield StatusPanel()

        with Horizontal(id="button-container"):
            yield Button("Status (s)", variant="primary", id="btn-status")
            yield Button("Files (f)", variant="success", id="btn-files")
            yield Button("Managed (m)", variant="success", id="btn-managed")
            yield Button("Diff (v)", variant="primary", id="btn-diff")
            yield Button("Data (t)", variant="default", id="btn-data")
            yield Button("Doctor (c)", variant="default", id="btn-doctor")
            yield Button("Quit (q)", variant="error", id="btn-quit")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app enters application mode."""
        self.title = "Chezmoi Manager v0.1.0"
        self.sub_title = "Use keyboard shortcuts or click buttons to navigate"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-quit":
            self.exit()
        elif button_id == "btn-status":
            self.action_show_status()
        elif button_id == "btn-files":
            self.action_show_files()
        elif button_id == "btn-managed":
            self.action_show_managed()
        elif button_id == "btn-diff":
            self.action_show_diff()
        elif button_id == "btn-data":
            self.action_show_data()
        elif button_id == "btn-doctor":
            self.action_show_doctor()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_show_status(self) -> None:
        """Show the status screen."""
        self.push_screen(StatusScreen())

    def action_show_files(self) -> None:
        """Show the file browser screen."""
        self.push_screen(FileBrowserScreen())

    def action_show_diff(self) -> None:
        """Show the diff viewer screen."""
        self.push_screen(DiffViewerScreen())

    def action_show_managed(self) -> None:
        """Show the managed files table screen."""
        self.push_screen(ManagedFilesScreen())

    def action_show_data(self) -> None:
        """Show the template data screen."""
        self.push_screen(TemplateDataScreen())

    def action_show_doctor(self) -> None:
        """Show the doctor diagnostics screen."""
        self.push_screen(DoctorScreen())


def main() -> None:
    """Run the Chezmoi Manager application."""
    app = ChezmoiManager()
    app.run()


if __name__ == "__main__":
    main()
