"""Screen for listing managed files."""

from textual.widgets import ListView, ListItem, Label
from textual.containers import Container
from textual import on

from ..base_screen import BaseScreen
from ..chezmoi_wrapper import ChezmoiWrapper, ChezmoiCommandError


class ListScreen(BaseScreen):
    """Screen for listing managed files."""
    
    CSS = """
    ListScreen {
        align: center middle;
    }
    
    #list_container {
        width: 80;
        height: 30;
        border: solid $primary;
        padding: 1;
    }
    
    ListView {
        height: 1fr;
    }
    """
    
    def __init__(self, chezmoi: ChezmoiWrapper, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chezmoi = chezmoi
    
    def compose(self):
        """Compose the screen."""
        with Container(id="list_container"):
            yield Label("Managed Files")
            yield ListView()
    
    def on_mount(self) -> None:
        """Handle mount."""
        self._load_files()
    
    def _load_files(self) -> None:
        """Load files."""
        try:
            files = self.chezmoi.managed()
            list_view = self.query_one(ListView)
            list_view.clear()
            for file_path in files:
                list_view.append(ListItem(Label(file_path)))
        except ChezmoiCommandError:
            pass
