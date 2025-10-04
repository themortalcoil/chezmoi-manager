"""Chezmoi doctor diagnostic screen."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, RichLog, Static
from textual.worker import Worker, WorkerState

from chezmoi import ChezmoiWrapper


class DoctorScreen(Screen):
    """Screen for running chezmoi doctor diagnostics."""

    CSS = """
    DoctorScreen {
        align: center top;
    }

    #doctor-container {
        width: 95%;
        height: 1fr;
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        margin: 1;
    }

    #doctor-title {
        padding: 1 0;
        text-style: bold;
    }

    RichLog {
        height: 1fr;
        border: solid $accent;
        background: $surface;
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
        ("r", "refresh", "Run Again"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Vertical(id="doctor-container"):
            yield Static("[bold]Chezmoi Doctor[/bold]", id="doctor-title")
            yield Static(
                "[dim]Running diagnostics...[/dim]", classes="loading", id="loading"
            )
            yield RichLog(id="doctor-log", wrap=True, highlight=True, markup=True)

        with Vertical(id="actions-container"):
            yield Button("Run Again", variant="primary", id="btn-run")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.title = "Chezmoi Doctor"
        self.sub_title = "System diagnostics - Press 'r' to run again, 'esc' to go back"

        # Hide log initially
        log = self.query_one("#doctor-log", RichLog)
        log.display = False

        # Run doctor
        self.run_doctor()

    def run_doctor(self) -> None:
        """Run doctor diagnostics in background worker."""
        self.run_worker(self._fetch_doctor_output, exclusive=True, thread=True)

    async def _fetch_doctor_output(self) -> str:
        """Fetch doctor output from chezmoi."""
        try:
            return ChezmoiWrapper.doctor()
        except Exception as e:
            return f"Error running doctor: {e}"

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result is not None:
                self.update_log(event.worker.result)

    def update_log(self, output: str) -> None:
        """Update log with doctor output."""
        # Hide loading message
        loading = self.query_one("#loading", Static)
        loading.display = False

        # Show and update log
        log = self.query_one("#doctor-log", RichLog)
        log.display = True
        log.clear()

        if output.strip():
            # Parse and colorize output
            lines = output.split("\n")
            for line in lines:
                if "OK" in line or "ok" in line:
                    log.write(f"[green]{line}[/green]")
                elif "WARNING" in line or "warning" in line.lower():
                    log.write(f"[yellow]{line}[/yellow]")
                elif "ERROR" in line or "error" in line.lower():
                    log.write(f"[red]{line}[/red]")
                elif line.startswith("  "):
                    log.write(f"[dim]{line}[/dim]")
                else:
                    log.write(line)
        else:
            log.write("[yellow]No output from chezmoi doctor[/yellow]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-run":
            self.action_refresh()

    def action_refresh(self) -> None:
        """Re-run doctor diagnostics."""
        # Show loading
        loading = self.query_one("#loading", Static)
        loading.display = True

        log = self.query_one("#doctor-log", RichLog)
        log.display = False

        self.run_doctor()
        self.app.notify("Running diagnostics...", timeout=1)

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
