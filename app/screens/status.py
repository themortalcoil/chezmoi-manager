"""Status screen showing detailed chezmoi status."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static
from textual.worker import Worker, WorkerState

from chezmoi import ChezmoiWrapper


class StatusDisplay(Static):
    """Widget to display chezmoi status output."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Chezmoi Status[/bold]")
        yield Label("")
        yield Label("[dim]Loading status...[/dim]", id="status-content")

    def on_mount(self) -> None:
        """Load status when mounted."""
        self.load_status()

    def load_status(self) -> None:
        """Load status in background worker."""
        self.run_worker(self._fetch_status, exclusive=True, thread=True)

    async def _fetch_status(self) -> str:
        """Fetch status from chezmoi."""
        try:
            return ChezmoiWrapper.get_status()
        except Exception as e:
            return f"Error loading status: {e}"

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result:
                self.update_status(event.worker.result)

    def update_status(self, status: str) -> None:
        """Update status display."""
        content = self.query_one("#status-content", Label)
        if status.strip():
            # Status output exists - show it
            content.update(f"[cyan]{status}[/cyan]")
        else:
            # No changes
            content.update(
                "[green]✓ No pending changes - everything is in sync[/green]"
            )


class StatusScreen(Screen):
    """Screen for viewing chezmoi status."""

    CSS = """
    StatusScreen {
        align: center top;
    }

    #status-container {
        width: 90%;
        height: auto;
        max-height: 80%;
        background: $panel;
        border: solid $primary;
        padding: 2 4;
        margin: 2;
    }

    #status-actions {
        width: 90%;
        height: auto;
        align: center middle;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("r", "refresh", "Refresh"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Vertical(id="status-container"):
            yield StatusDisplay()

        with Vertical(id="status-actions"):
            yield Button("Refresh", variant="primary", id="btn-refresh")
            yield Button("View Files", variant="success", id="btn-files")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.sub_title = "Press 'r' to refresh, 'esc' to go back"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-files":
            self.app.notify("File browser coming soon!", title="Info")

    def action_refresh(self) -> None:
        """Refresh the status display."""
        status_widget = self.query_one(StatusDisplay)
        status_widget.load_status()
        self.app.notify("Refreshing status...", timeout=1)

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
