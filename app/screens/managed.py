"""Managed files screen with DataTable view."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static
from textual.worker import Worker, WorkerState

from chezmoi import ChezmoiWrapper


class ManagedFilesScreen(Screen):
    """Screen for viewing managed files in a table."""

    CSS = """
    ManagedFilesScreen {
        align: center top;
    }

    #table-container {
        width: 95%;
        height: 1fr;
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        margin: 1;
    }

    #table-title {
        padding: 1 0;
        text-style: bold;
    }

    DataTable {
        height: 1fr;
    }

    #actions-container {
        dock: bottom;
        height: auto;
        width: 95%;
        padding: 1 2;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    .loading {
        text-align: center;
        padding: 2;
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

        with Vertical(id="table-container"):
            yield Static("[bold]Managed Files[/bold]", id="table-title")
            yield Static(
                "[dim]Loading managed files...[/dim]", classes="loading", id="loading"
            )
            yield DataTable(id="files-table", zebra_stripes=True)

        with Vertical(id="actions-container"):
            yield Button("Refresh", variant="primary", id="btn-refresh")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.title = "Managed Files"
        self.sub_title = "Press 'r' to refresh, 'esc' to go back"

        # Hide table initially
        table = self.query_one("#files-table", DataTable)
        table.display = False

        # Load files
        self.load_files()

    def load_files(self) -> None:
        """Load managed files in background worker."""
        self.run_worker(self._fetch_files, exclusive=True, thread=True)

    async def _fetch_files(self) -> list[str]:
        """Fetch managed files from chezmoi."""
        try:
            return ChezmoiWrapper.get_managed_files()
        except Exception as e:
            self.app.notify(f"Error loading files: {e}", severity="error")
            return []

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result is not None:
                self.update_table(event.worker.result)

    def update_table(self, files: list[str]) -> None:
        """Update table with managed files."""
        # Hide loading message
        loading = self.query_one("#loading", Static)
        loading.display = False

        # Show and populate table
        table = self.query_one("#files-table", DataTable)
        table.display = True
        table.clear(columns=True)

        if not files:
            # Update title to show no files
            title = self.query_one("#table-title", Static)
            title.update(
                "[bold]Managed Files[/bold] - [yellow]No files managed[/yellow]"
            )
            return

        # Add columns
        table.add_columns("#", "File Path")

        # Add rows
        for idx, file_path in enumerate(files, 1):
            table.add_row(str(idx), file_path)

        # Update title with count
        title = self.query_one("#table-title", Static)
        title.update(f"[bold]Managed Files[/bold] - [cyan]{len(files)} files[/cyan]")

        # Focus the table
        table.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-refresh":
            self.action_refresh()

    def action_refresh(self) -> None:
        """Refresh the table."""
        # Show loading
        loading = self.query_one("#loading", Static)
        loading.display = True

        table = self.query_one("#files-table", DataTable)
        table.display = False

        self.load_files()
        self.app.notify("Refreshing file list...", timeout=1)

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        table = event.data_table
        row = table.get_row(event.row_key)
        file_path = row[1]  # Get file path from second column

        self.app.notify(f"Selected: {file_path}", timeout=2)
