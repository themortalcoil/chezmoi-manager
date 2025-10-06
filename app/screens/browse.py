"""Screen for browsing and selecting files."""

from pathlib import Path
from textual.widgets import DirectoryTree, Button, Label
from textual.containers import Container, Vertical
from textual import on

from ..base_screen import BaseScreen
from ..chezmoi_wrapper import ChezmoiWrapper
from ..constants import BUTTON_CANCEL


class FileBrowserScreen(BaseScreen):
    """Screen for browsing files."""
    
    CSS = """
    FileBrowserScreen {
        align: center middle;
    }
    
    #browser_container {
        width: 80;
        height: 30;
        border: solid $primary;
        padding: 1;
    }
    
    DirectoryTree {
        height: 1fr;
    }
    
    .button-row {
        layout: horizontal;
        height: auto;
        align: center middle;
        margin: 1 0;
    }
    
    .button-row Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, chezmoi: ChezmoiWrapper, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chezmoi = chezmoi
    
    def compose(self):
        """Compose the screen."""
        with Container(id="browser_container"):
            yield Label("Select a file")
            yield DirectoryTree(str(Path.home()))
            from textual.containers import Horizontal
            with Horizontal(classes="button-row"):
                yield Button("Cancel", id=BUTTON_CANCEL)
    
    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        self.dismiss(str(event.path))
    
    @on(Button.Pressed, f"#{BUTTON_CANCEL}")
    def on_cancel(self) -> None:
        """Handle cancel."""
        self.dismiss(None)
