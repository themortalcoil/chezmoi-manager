"""Screen for removing files from chezmoi."""

from textual.widgets import Button, Label
from textual.containers import Container, Horizontal
from textual import on

from ..base_screen import BaseScreen
from ..chezmoi_wrapper import ChezmoiWrapper
from ..widgets import FileInput, ResultPanel
from ..constants import BUTTON_SUBMIT, BUTTON_CANCEL


class RemoveScreen(BaseScreen):
    """Screen for removing files."""
    
    CSS = """
    RemoveScreen {
        align: center middle;
    }
    
    #remove_container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 1;
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
        with Container(id="remove_container"):
            yield Label("Remove File from Chezmoi")
            yield FileInput(id="file_input")
            yield ResultPanel(id="result_panel")
            with Horizontal(classes="button-row"):
                yield Button("Remove", variant="error", id=BUTTON_SUBMIT)
                yield Button("Cancel", id=BUTTON_CANCEL)
    
    @on(Button.Pressed, f"#{BUTTON_SUBMIT}")
    def on_submit(self) -> None:
        """Handle submit."""
        file_input = self.query_one("#file_input", FileInput)
        result_panel = self.query_one("#result_panel", ResultPanel)
        
        try:
            self.chezmoi.remove(file_input.value)
            result_panel.show_success("File removed successfully!")
            file_input.value = ""
        except Exception as e:
            result_panel.show_error(str(e))
    
    @on(Button.Pressed, f"#{BUTTON_CANCEL}")
    def on_cancel(self) -> None:
        """Handle cancel."""
        self.app.pop_screen()
