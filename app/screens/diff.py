"""Diff viewer screen for viewing changes."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, TextArea
from textual.worker import Worker, WorkerState

from app.widgets.confirm import ConfirmDialog
from chezmoi import ChezmoiWrapper


class DiffViewerScreen(Screen):
    """Screen for viewing diffs."""

    CSS = """
    DiffViewerScreen {
        align: center top;
    }

    #diff-container {
        width: 95%;
        height: 1fr;
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        margin: 1;
    }

    #diff-title {
        padding: 1 0;
        text-style: bold;
    }

    TextArea {
        height: 1fr;
        border: solid $accent;
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
        ("a", "apply", "Apply Changes"),
        ("q", "app.quit", "Quit"),
    ]

    def __init__(self, target: str = "") -> None:
        """Initialize the diff viewer.

        Args:
            target: Specific file to show diff for (empty for all files).
        """
        super().__init__()
        self.target = target

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Vertical(id="diff-container"):
            title = f"Diff: {self.target}" if self.target else "Diff: All Files"
            yield Static(f"[bold]{title}[/bold]", id="diff-title")
            yield Static("[dim]Loading diff...[/dim]", classes="loading", id="loading")
            yield TextArea(
                "",
                language="diff",
                theme="monokai",
                read_only=True,
                show_line_numbers=True,
                id="diff-area",
            )

        with Vertical(id="actions-container"):
            yield Button("Apply Changes", variant="success", id="btn-apply")
            yield Button("Refresh", variant="primary", id="btn-refresh")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.title = "Diff Viewer"
        self.sub_title = "Press 'a' to apply, 'r' to refresh, 'esc' to go back"

        # Hide TextArea initially
        text_area = self.query_one("#diff-area", TextArea)
        text_area.display = False

        # Load diff
        self.load_diff()

    def load_diff(self) -> None:
        """Load diff in background worker."""
        self.run_worker(self._fetch_diff, exclusive=True, thread=True)

    async def _fetch_diff(self) -> str:
        """Fetch diff from chezmoi."""
        try:
            return ChezmoiWrapper.get_diff(self.target)
        except Exception as e:
            return f"Error loading diff: {e}"

    def update_diff(self, diff: str) -> None:
        """Update diff display."""
        # Hide loading message
        loading = self.query_one("#loading", Static)
        loading.display = False

        # Show and update TextArea
        text_area = self.query_one("#diff-area", TextArea)
        text_area.display = True

        if diff.strip():
            text_area.text = diff
        else:
            text_area.text = (
                "No changes detected.\n\nAll files are in sync with the target state."
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-apply":
            self.action_apply()

    def action_refresh(self) -> None:
        """Refresh the diff display."""
        # Show loading
        loading = self.query_one("#loading", Static)
        loading.display = True

        text_area = self.query_one("#diff-area", TextArea)
        text_area.display = False

        self.load_diff()
        self.app.notify("Refreshing diff...", timeout=1)

    def action_apply(self) -> None:
        """Apply changes (with confirmation)."""
        # Check if there are changes to apply
        text_area = self.query_one("#diff-area", TextArea)
        if "No changes detected" in text_area.text:
            self.app.notify("No changes to apply", severity="information")
            return

        # Show confirmation dialog
        self.app.push_screen(
            ConfirmDialog(
                title="Apply Changes?",
                message="This will apply all pending changes to your system.\n\nAre you sure you want to continue?",
                confirm_text="Apply",
                cancel_text="Cancel",
            ),
            self.handle_apply_confirm,
        )

    def handle_apply_confirm(self, confirmed: bool) -> None:
        """Handle apply confirmation result."""
        if confirmed:
            self.run_worker(self._apply_changes, exclusive=True, thread=True)
            self.app.notify("Applying changes...", timeout=2)
        else:
            self.app.notify("Apply cancelled", severity="information")

    async def _apply_changes(self) -> tuple[bool, str]:
        """Apply changes using chezmoi."""
        try:
            result = ChezmoiWrapper.apply(dry_run=False, verbose=True)
            return (True, result)
        except Exception as e:
            return (False, str(e))

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result is not None:
                # Check which worker completed
                if isinstance(event.worker.result, tuple):
                    # Apply worker
                    success, message = event.worker.result
                    if success:
                        self.app.notify(
                            "Changes applied successfully!",
                            severity="information",
                            timeout=3,
                        )
                        # Refresh the diff
                        self.load_diff()
                    else:
                        self.app.notify(
                            f"Apply failed: {message}",
                            severity="error",
                            timeout=5,
                        )
                else:
                    # Diff load worker
                    self.update_diff(event.worker.result)

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
