"""Screen for viewing and applying diffs."""

import re
from datetime import datetime
from pathlib import Path
from textual.widgets import Button, Label, Static, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual import on
from rich.syntax import Syntax

from ..base_screen import BaseScreen
from ..chezmoi_wrapper import ChezmoiWrapper, ChezmoiCommandError
from ..constants import BUTTON_APPLY, BUTTON_REFRESH, BUTTON_EXPORT


class StatisticsPanel(Static):
    """Panel showing diff statistics."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Statistics"
    
    def update_stats(self, files: int, additions: int, deletions: int) -> None:
        """Update statistics display."""
        net_change = additions - deletions
        net_symbol = "+" if net_change >= 0 else ""
        
        content = (
            f"[bold]Files changed:[/bold] {files}\n"
            f"[green]+{additions} additions[/green]\n"
            f"[red]-{deletions} deletions[/red]\n"
            f"[bold]Net change:[/bold] {net_symbol}{net_change}"
        )
        self.update(content)


class FileListPanel(ListView):
    """Panel showing changed files."""
    
    def update_files(self, files: list[str]) -> None:
        """Update the file list."""
        self.clear()
        for file_path in files:
            item = ListItem(Label(file_path))
            item.file_path = file_path
            self.append(item)


class DiffScreen(BaseScreen):
    """Screen for viewing chezmoi diffs with enhanced features."""
    
    CSS = """
    DiffScreen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30;
        border-right: solid $primary;
        padding: 1;
    }
    
    #main_content {
        width: 1fr;
        padding: 1;
    }
    
    StatisticsPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
        margin-bottom: 1;
    }
    
    FileListPanel {
        border: solid $accent;
        height: 1fr;
    }
    
    #diff_container {
        border: solid $accent;
        height: 1fr;
        padding: 1;
    }
    
    #error_panel {
        border: solid red;
        padding: 1;
        height: auto;
        background: $error;
        margin: 1 0;
    }
    
    .button-row {
        layout: horizontal;
        height: auto;
        margin: 1 0;
    }
    
    .button-row Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        ("n", "next_change", "Next"),
        ("p", "prev_change", "Previous"),
        ("escape", "pop_screen", "Back"),
    ]
    
    def __init__(self, chezmoi: ChezmoiWrapper, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chezmoi = chezmoi
        self.current_diff = ""
        self.changed_files = []
        self.selected_file = None
    
    def compose(self):
        """Compose the screen."""
        with Vertical(id="sidebar"):
            yield StatisticsPanel(id="stats_panel")
            yield Label("Changed Files")
            yield FileListPanel(id="file_list")
        
        with Vertical(id="main_content"):
            yield Label("Diff: All Files", id="diff_title")
            yield Static(id="error_panel", classes="hidden")
            with VerticalScroll(id="diff_container"):
                yield Static(id="diff_display")
            
            with Horizontal(classes="button-row"):
                yield Button("🔄 Refresh", id=BUTTON_REFRESH)
                yield Button("✓ Apply All", variant="primary", id=BUTTON_APPLY)
                yield Button("💾 Export", id=BUTTON_EXPORT)
    
    def on_mount(self) -> None:
        """Handle mount event."""
        self._load_diff()
    
    def _load_diff(self, file_path: str | None = None) -> None:
        """Load diff."""
        try:
            diff_output = self.chezmoi.diff(file_path)
            self._update_display(diff_output, file_path)
        except ChezmoiCommandError as e:
            self._show_error(str(e))
    
    def _parse_diff(self, diff_text: str) -> tuple[list[str], int, int]:
        """Parse diff to extract files and statistics.
        
        Returns:
            Tuple of (files, additions, deletions)
        """
        files = []
        additions = 0
        deletions = 0
        
        # Extract files from diff headers
        for match in re.finditer(r'^diff --git a/(.*?) b/.*?$', diff_text, re.MULTILINE):
            files.append(match.group(1))
        
        # Count additions and deletions
        for line in diff_text.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        return files, additions, deletions
    
    def _update_display(self, diff_text: str, file_path: str | None = None) -> None:
        """Update the diff display."""
        self.current_diff = diff_text
        
        if not diff_text or not diff_text.strip():
            self.query_one("#diff_display").update("[dim]No changes to display[/dim]")
            self.query_one("#stats_panel", StatisticsPanel).update_stats(0, 0, 0)
            self.query_one("#file_list", FileListPanel).update_files([])
            return
        
        # Parse diff
        files, additions, deletions = self._parse_diff(diff_text)
        self.changed_files = files
        
        # Update statistics
        self.query_one("#stats_panel", StatisticsPanel).update_stats(
            len(files), additions, deletions
        )
        
        # Update file list
        self.query_one("#file_list", FileListPanel).update_files(files)
        
        # Update title
        title = f"Diff: {file_path}" if file_path else "Diff: All Files"
        self.query_one("#diff_title").update(title)
        
        # Render diff with syntax highlighting
        try:
            syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
            self.query_one("#diff_display").update(syntax)
        except Exception:
            # Fallback to plain text
            self.query_one("#diff_display").update(diff_text)
        
        # Hide error panel
        self.query_one("#error_panel").add_class("hidden")
    
    def _show_error(self, error: str) -> None:
        """Show an error message."""
        error_panel = self.query_one("#error_panel")
        error_panel.update(f"[red]Error:[/red] {error}\n[dim]Suggestions: Check chezmoi status, ensure chezmoi is initialized[/dim]")
        error_panel.remove_class("hidden")
        self.query_one("#diff_display").update("")
    
    @on(ListView.Selected)
    def on_file_selected(self, event: ListView.Selected) -> None:
        """Handle file selection from list."""
        if event.item and hasattr(event.item, 'file_path'):
            self.selected_file = event.item.file_path
            self._load_diff(self.selected_file)
    
    @on(Button.Pressed, f"#{BUTTON_REFRESH}")
    def on_refresh(self) -> None:
        """Handle refresh button."""
        self.selected_file = None
        self._load_diff()
    
    @on(Button.Pressed, f"#{BUTTON_APPLY}")
    def on_apply(self) -> None:
        """Handle apply button."""
        self._apply_changes(self.selected_file)
    
    def _apply_changes(self, file_path: str | None = None) -> None:
        """Apply changes."""
        try:
            self.chezmoi.apply(file_path)
            self._handle_apply_complete(True, file_path)
        except ChezmoiCommandError as e:
            self._handle_apply_complete(False, file_path, str(e))
    
    def _handle_apply_complete(self, success: bool, file_path: str | None = None, error: str = "") -> None:
        """Handle apply completion."""
        error_panel = self.query_one("#error_panel")
        
        if success:
            target = file_path or "all files"
            error_panel.update(f"[green]✓ Successfully applied changes to {target}[/green]")
            error_panel.remove_class("hidden")
            # Reload diff
            self._load_diff()
        else:
            self._show_error(f"Failed to apply: {error}")
    
    @on(Button.Pressed, f"#{BUTTON_EXPORT}")
    def on_export(self) -> None:
        """Handle export button."""
        if not self.current_diff:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/chezmoi_diff_{timestamp}.patch"
        
        try:
            Path(filename).write_text(self.current_diff)
            error_panel = self.query_one("#error_panel")
            error_panel.update(f"[green]✓ Exported to {filename}[/green]")
            error_panel.remove_class("hidden")
        except Exception as e:
            self._show_error(f"Failed to export: {e}")
    
    def action_next_change(self) -> None:
        """Jump to next change."""
        # This would require more complex diff parsing
        pass
    
    def action_prev_change(self) -> None:
        """Jump to previous change."""
        # This would require more complex diff parsing
        pass

