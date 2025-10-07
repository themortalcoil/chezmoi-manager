"""Screen for editing managed files."""

from textual.widgets import Button, Label
from textual.containers import Container, Horizontal
from textual import on

from ..base_screen import BaseScreen
from ..chezmoi_wrapper import ChezmoiWrapper
from ..widgets import FileInput
from ..constants import BUTTON_CANCEL


class EditScreen(BaseScreen):
    """Screen for editing files."""
    
    CSS = """
    EditScreen {
        align: center middle;
    }
    
    #edit_container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """
    
    def __init__(self, chezmoi: ChezmoiWrapper, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chezmoi = chezmoi
    
    def compose(self):
        """Compose the screen."""
        with Container(id="edit_container"):
            yield Label("Edit feature coming soon!")
            with Horizontal():
                yield Button("Back", id=BUTTON_CANCEL)
    
    @on(Button.Pressed, f"#{BUTTON_CANCEL}")
    def on_cancel(self) -> None:
        """Handle cancel."""
        self.app.pop_screen()
