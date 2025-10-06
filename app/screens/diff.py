"""Diff viewer screen for viewing changes."""

import re
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListView,
    ListItem,
    Static,
    TextArea,
)
from textual.worker import Worker, WorkerState

from app.widgets.confirm import ConfirmDialog
from chezmoi import ChezmoiWrapper, ChezmoiCommandError


class DiffStatsPanel(Static):
    """Panel showing diff statistics."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Statistics[/bold]", id="stats-title")
        yield Label("", id="stats-content")

    def update_stats(self, diff: str) -> None:
        """Update statistics from diff content.

        Args:
            diff: The diff content to analyze.
        """
        if not diff.strip():
            self.query_one("#stats-content", Label).update(
                "[dim]No changes to analyze[/dim]"
            )
            return

        # Parse diff for statistics
        lines = diff.split("\n")
        files_changed = set()
        additions = 0
        deletions = 0

        for line in lines:
            # Count file changes (lines starting with diff or ---)
            if line.startswith("diff --git"):
                # Extract filename from diff --git a/file b/file
                match = re.search(r"diff --git a/(.*?) b/", line)
                if match:
                    files_changed.add(match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        stats_lines = [
            f"[cyan]Files changed:[/cyan] {len(files_changed)}",
            f"[green]Lines added:[/green] +{additions}",
            f"[red]Lines deleted:[/red] -{deletions}",
            f"[yellow]Net change:[/yellow] {additions - deletions:+d}",
        ]

        self.query_one("#stats-content", Label).update("\n".join(stats_lines))


class FileListPanel(Static):
    """Panel for selecting specific files to view diff."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Changed Files[/bold]", id="file-list-title")
        yield Label("[dim]Loading files...[/dim]", id="file-list-loading")
        with VerticalScroll(id="file-list-scroll"):
            yield ListView(id="file-list")

    def update_files(self, files: list[str]) -> None:
        """Update file list.

        Args:
            files: List of changed files.
        """
        loading = self.query_one("#file-list-loading", Label)
        loading.display = False

        list_view = self.query_one("#file-list", ListView)
        list_view.clear()

        if not files:
            list_view.display = False
            loading.update("[dim]No changed files[/dim]")
            loading.display = True
            return

        list_view.display = True
        for file in files:
            item = ListItem(Label(file))
            item.file_path = file
            list_view.append(item)


class DiffViewerScreen(Screen):
    """Screen for viewing diffs."""

    CSS = """
    DiffViewerScreen {
        align: center top;
        layout: horizontal;
    }

    #sidebar {
        width: 30;
        height: 1fr;
        background: $panel;
        border: solid $primary;
        padding: 1;
        margin: 1;
        dock: left;
    }

    DiffStatsPanel {
        width: 100%;
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $accent;
    }

    FileListPanel {
        width: 100%;
        height: 1fr;
        padding: 1;
        border: solid $success;
    }

    #file-list-scroll {
        height: 1fr;
        border: none;
    }

    #file-list {
        height: auto;
    }

    #main-content {
        width: 1fr;
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

    #error-panel {
        padding: 2;
        background: $error 20%;
        border: solid $error;
        margin: 1 0;
    }

    TextArea {
        height: 1fr;
        border: solid $accent;
        margin-top: 1;
    }

    #actions-container {
        dock: bottom;
        height: auto;
        width: 100%;
        padding: 1 2;
        align: center middle;
        background: $surface;
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
        ("e", "export", "Export Diff"),
        ("n", "next_change", "Next Change"),
        ("p", "prev_change", "Prev Change"),
        ("q", "app.quit", "Quit"),
    ]

    def __init__(self, target: str = "") -> None:
        """Initialize the diff viewer.

        Args:
            target: Specific file to show diff for (empty for all files).
        """
        super().__init__()
        self.target = target
        self.changed_files: list[str] = []
        self.current_diff = ""
        self.has_error = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        # Sidebar with stats and file list
        with Vertical(id="sidebar"):
            yield DiffStatsPanel()
            yield FileListPanel()

        # Main content area
        with Vertical(id="main-content"):
            title = f"Diff: {self.target}" if self.target else "Diff: All Files"
            yield Static(f"[bold]{title}[/bold]", id="diff-title")
            yield Static("[dim]Loading diff...[/dim]", classes="loading", id="loading")
            yield Static("", id="error-panel")  # Hidden by default
            yield TextArea(
                "",
                language="diff",
                theme="monokai",
                read_only=True,
                show_line_numbers=True,
                id="diff-area",
            )

        # Action buttons at bottom
        with Horizontal(id="actions-container"):
            yield Button("🔄 Refresh (r)", variant="primary", id="btn-refresh")
            yield Button("✓ Apply (a)", variant="success", id="btn-apply")
            yield Button("💾 Export (e)", variant="default", id="btn-export")
            yield Button("← Back (esc)", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.title = "Diff Viewer"
        self.sub_title = (
            "Press 'a' to apply, 'r' to refresh, 'e' to export, 'esc' to go back"
        )

        # Hide panels initially
        text_area = self.query_one("#diff-area", TextArea)
        text_area.display = False

        error_panel = self.query_one("#error-panel", Static)
        error_panel.display = False

        # Load diff
        self.load_diff()

    def show_error(self, error_msg: str, details: str = "") -> None:
        """Show error message in error panel.

        Args:
            error_msg: Main error message.
            details: Optional detailed error information.
        """
        self.has_error = True
        error_panel = self.query_one("#error-panel", Static)

        error_text = f"[red bold]✗ Error:[/red bold] {error_msg}"
        if details:
            error_text += f"\n\n[dim]{details}[/dim]"

        error_text += "\n\n[yellow]💡 Suggestions:[/yellow]"
        error_text += "\n• Check that chezmoi is properly configured"
        error_text += "\n• Run 'chezmoi doctor' to diagnose issues"
        error_text += "\n• Press 'r' to retry loading the diff"

        error_panel.update(error_text)
        error_panel.display = True

    def hide_error(self) -> None:
        """Hide error panel."""
        self.has_error = False
        error_panel = self.query_one("#error-panel", Static)
        error_panel.display = False

    def load_diff(self) -> None:
        """Load diff in background worker."""
        self.hide_error()
        self.run_worker(self._fetch_diff, exclusive=True, thread=True)

    async def _fetch_diff(self) -> tuple[bool, str, str]:
        """Fetch diff from chezmoi.

        Returns:
            tuple[bool, str, str]: (success, diff_content, error_message)
        """
        try:
            diff_content = ChezmoiWrapper.get_diff(self.target)
            return (True, diff_content, "")
        except ChezmoiCommandError as e:
            error_msg = "Failed to get diff from chezmoi"
            details = f"{str(e)}\n\nStderr: {e.stderr}" if e.stderr else str(e)
            return (False, "", f"{error_msg}\n\n{details}")
        except Exception as e:
            return (False, "", f"Unexpected error: {type(e).__name__}: {str(e)}")

    def update_diff(self, success: bool, diff: str, error: str) -> None:
        """Update diff display.

        Args:
            success: Whether the diff fetch was successful.
            diff: The diff content.
            error: Error message if not successful.
        """
        # Hide loading message
        loading = self.query_one("#loading", Static)
        loading.display = False

        if not success:
            self.show_error("Failed to load diff", error)
            text_area = self.query_one("#diff-area", TextArea)
            text_area.display = False
            return

        # Hide error panel if previously shown
        self.hide_error()

        # Show and update TextArea
        text_area = self.query_one("#diff-area", TextArea)
        text_area.display = True

        if diff.strip():
            self.current_diff = diff
            text_area.text = diff

            # Update stats panel
            stats_panel = self.query_one(DiffStatsPanel)
            stats_panel.update_stats(diff)

            # Extract and update file list
            self.changed_files = self._extract_changed_files(diff)
            file_list_panel = self.query_one(FileListPanel)
            file_list_panel.update_files(self.changed_files)

            self.app.notify(
                f"Loaded diff with {len(self.changed_files)} changed file(s)",
                severity="information",
            )
        else:
            self.current_diff = ""
            text_area.text = (
                "✓ No changes detected.\n\n"
                "All files are in sync with the target state.\n\n"
                "[dim]Your dotfiles are up to date![/dim]"
            )
            stats_panel = self.query_one(DiffStatsPanel)
            stats_panel.update_stats("")

            file_list_panel = self.query_one(FileListPanel)
            file_list_panel.update_files([])

            self.app.notify("No changes detected", severity="information")

    def _extract_changed_files(self, diff: str) -> list[str]:
        """Extract list of changed files from diff.

        Args:
            diff: The diff content.

        Returns:
            List of file paths that have changes.
        """
        files = []
        for line in diff.split("\n"):
            if line.startswith("diff --git"):
                match = re.search(r"diff --git a/(.*?) b/", line)
                if match:
                    files.append(match.group(1))
        return files

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-apply":
            self.action_apply()
        elif button_id == "btn-export":
            self.action_export()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle file selection from list."""
        if event.item and hasattr(event.item, "file_path"):
            file_path = event.item.file_path
            # Reload diff with specific file
            self.target = file_path
            title = self.query_one("#diff-title", Static)
            title.update(f"[bold]Diff: {file_path}[/bold]")
            self.load_diff()

            self.app.notify(
                f"Showing diff for: {file_path}",
                severity="information",
            )

    def action_refresh(self) -> None:
        """Refresh the diff display."""
        # Show loading
        loading = self.query_one("#loading", Static)
        loading.display = True

        text_area = self.query_one("#diff-area", TextArea)
        text_area.display = False

        # Reset target to show all files
        if self.target:
            self.target = ""
            title = self.query_one("#diff-title", Static)
            title.update("[bold]Diff: All Files[/bold]")

        self.load_diff()
        self.app.notify("Refreshing diff...", timeout=1)

    def action_export(self) -> None:
        """Export diff to file."""
        if not self.current_diff:
            self.app.notify("No diff to export", severity="warning")
            return

        try:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chezmoi_diff_{timestamp}.patch"
            filepath = Path.home() / filename

            with open(filepath, "w") as f:
                f.write(self.current_diff)

            self.app.notify(
                f"✓ Diff exported to: {filepath}",
                title="Export Successful",
                severity="information",
                timeout=5,
            )
        except Exception as e:
            self.app.notify(
                f"Failed to export diff: {e}",
                title="Export Failed",
                severity="error",
                timeout=5,
            )

    def action_next_change(self) -> None:
        """Jump to next change in diff."""
        text_area = self.query_one("#diff-area", TextArea)
        if not text_area.display:
            return

        # Find next line starting with + or -
        current_line = text_area.cursor_location[0]
        lines = text_area.text.split("\n")

        for i in range(current_line + 1, len(lines)):
            if lines[i].startswith("+") or lines[i].startswith("-"):
                text_area.cursor_location = (i, 0)
                self.app.notify(f"Line {i + 1}", timeout=1)
                return

        self.app.notify("No more changes", severity="information", timeout=1)

    def action_prev_change(self) -> None:
        """Jump to previous change in diff."""
        text_area = self.query_one("#diff-area", TextArea)
        if not text_area.display:
            return

        # Find previous line starting with + or -
        current_line = text_area.cursor_location[0]
        lines = text_area.text.split("\n")

        for i in range(current_line - 1, -1, -1):
            if lines[i].startswith("+") or lines[i].startswith("-"):
                text_area.cursor_location = (i, 0)
                self.app.notify(f"Line {i + 1}", timeout=1)
                return

        self.app.notify("No more changes", severity="information", timeout=1)

    def action_apply(self) -> None:
        """Apply changes (with confirmation)."""
        if self.has_error:
            self.app.notify(
                "Cannot apply changes while there's an error", severity="warning"
            )
            return

        # Check if there are changes to apply
        if not self.current_diff:
            self.app.notify("No changes to apply", severity="information")
            return

        # Build confirmation message
        num_files = len(self.changed_files)
        if self.target:
            message = f"This will apply changes to:\n  {self.target}\n\nAre you sure?"
        else:
            message = (
                f"This will apply changes to {num_files} file(s):\n"
                f"{chr(10).join('  • ' + f for f in self.changed_files[:5])}"
            )
            if num_files > 5:
                message += f"\n  ... and {num_files - 5} more"
            message += "\n\nAre you sure you want to continue?"

        # Show confirmation dialog
        self.app.push_screen(
            ConfirmDialog(
                title="Apply Changes?",
                message=message,
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

    async def _apply_changes(self) -> tuple[bool, str, str]:
        """Apply changes using chezmoi.

        Returns:
            tuple[bool, str, str]: (success, result, error_message)
        """
        try:
            targets = [self.target] if self.target else None
            result = ChezmoiWrapper.apply(targets=targets, dry_run=False, verbose=True)
            return (True, result, "")
        except ChezmoiCommandError as e:
            error_msg = f"{str(e)}\n\nStderr: {e.stderr}" if e.stderr else str(e)
            return (False, "", error_msg)
        except Exception as e:
            return (False, "", f"Unexpected error: {type(e).__name__}: {str(e)}")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result is not None:
                result = event.worker.result

                # Check which worker completed by the result type
                if isinstance(result, tuple):
                    if len(result) == 3:
                        # Could be diff worker or apply worker
                        success, content, error = result

                        if success and not error and content:
                            # This is likely a diff load
                            self.update_diff(True, content, "")
                        elif success and not content:
                            # This is likely an apply success
                            self.app.notify(
                                "✓ Changes applied successfully!",
                                title="Apply Complete",
                                severity="information",
                                timeout=3,
                            )
                            # Refresh the diff to show updated state
                            self.action_refresh()
                        else:
                            # This is an error from either worker
                            if "apply" in error.lower():
                                self.app.notify(
                                    f"Apply failed: {error}",
                                    title="Apply Error",
                                    severity="error",
                                    timeout=5,
                                )
                            else:
                                self.update_diff(False, "", error)

        elif event.state == WorkerState.ERROR:
            error_msg = (
                str(event.worker.error) if event.worker.error else "Unknown error"
            )
            self.show_error("Worker failed", error_msg)
            self.app.notify(
                "An error occurred",
                severity="error",
                timeout=3,
            )

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
