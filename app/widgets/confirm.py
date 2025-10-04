"""Confirmation dialog widget."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ConfirmDialog(ModalScreen[bool]):
    """A modal confirmation dialog."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    #dialog-container {
        width: 60;
        height: auto;
        background: $panel;
        border: solid $error;
        padding: 2;
    }

    #dialog-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding: 0 0 1 0;
        color: $error;
    }

    #dialog-message {
        width: 100%;
        padding: 1 0;
    }

    #dialog-buttons {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1 0 0 0;
    }

    #dialog-buttons Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        title: str = "Confirm",
        message: str = "Are you sure?",
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
    ) -> None:
        """Initialize the dialog.

        Args:
            title: Dialog title.
            message: Confirmation message.
            confirm_text: Text for confirm button.
            cancel_text: Text for cancel button.
        """
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Vertical(id="dialog-container"):
            yield Static(self.dialog_title, id="dialog-title")
            yield Label(self.dialog_message, id="dialog-message")

            with Horizontal(id="dialog-buttons"):
                yield Button(self.confirm_text, variant="error", id="btn-confirm")
                yield Button(self.cancel_text, variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_mount(self) -> None:
        """Focus cancel button on mount."""
        cancel_btn = self.query_one("#btn-cancel", Button)
        cancel_btn.focus()
