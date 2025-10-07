"""Base screen class for common functionality."""

from textual.screen import Screen


class BaseScreen(Screen):
    """Base class for all screens with common bindings and methods."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
    ]
    
    def action_pop_screen(self) -> None:
        """Pop the current screen and return to the previous one."""
        self.app.pop_screen()
