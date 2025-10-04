"""Chezmoi Manager - A TUI for managing chezmoi dotfiles."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header, Label, Static
from textual.binding import Binding

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
            yield Button("View Status", variant="primary", id="btn-status")
            yield Button("Managed Files", variant="success", id="btn-files")
            yield Button("Quit", variant="error", id="btn-quit")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app enters application mode."""
        self.title = "Chezmoi Manager v0.1.0"
        self.sub_title = "Press 'q' to quit, 'd' to toggle dark mode"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-quit":
            self.exit()
        elif button_id == "btn-status":
            self.notify("Status view coming soon!", title="Info")
        elif button_id == "btn-files":
            self.notify("File browser coming soon!", title="Info")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def main() -> None:
    """Run the Chezmoi Manager application."""
    app = ChezmoiManager()
    app.run()


if __name__ == "__main__":
    main()
