"""Main application for chezmoi-manager."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Container, Vertical
from textual import on

from app.chezmoi_wrapper import ChezmoiWrapper
from app.constants import (
    VERSION,
    APP_NAME,
    BUTTON_ADD,
    BUTTON_DIFF,
    BUTTON_EDIT,
    BUTTON_REMOVE,
    BUTTON_LIST,
)


class ChezmoiManager(App):
    """Main application for managing chezmoi dotfiles."""
    
    CSS = """
    ChezmoiManager {
        background: $surface;
    }
    
    #main_container {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    #menu_container {
        width: 50;
        height: auto;
        border: solid $primary;
        padding: 2;
        background: $panel;
    }
    
    #title {
        text-align: center;
        margin: 1 0;
        color: $accent;
    }
    
    #version {
        text-align: center;
        margin: 1 0;
        color: $text-muted;
    }
    
    .menu-buttons {
        layout: vertical;
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    .menu-buttons Button {
        margin: 1 0;
        width: 100%;
        max-width: 40;
    }
    """
    
    TITLE = APP_NAME
    SUB_TITLE = VERSION
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "show_diff", "Diff"),
    ]
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.chezmoi = ChezmoiWrapper()
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(id="main_container"):
            with Vertical(id="menu_container"):
                yield Static(f"[bold]{APP_NAME}[/bold]", id="title")
                yield Static(f"[dim]{VERSION}[/dim]", id="version")
                
                with Vertical(classes="menu-buttons"):
                    yield Button("📝 Add File", variant="primary", id=BUTTON_ADD)
                    yield Button("🔍 View Diff", id=BUTTON_DIFF)
                    yield Button("✏️  Edit File", id=BUTTON_EDIT)
                    yield Button("🗑️  Remove File", id=BUTTON_REMOVE)
                    yield Button("📋 List Files", id=BUTTON_LIST)
        
        yield Footer()
    
    @on(Button.Pressed, f"#{BUTTON_ADD}")
    def action_show_add(self) -> None:
        """Show add file screen."""
        from app.screens.add import AddDotfileScreen
        self.push_screen(AddDotfileScreen(self.chezmoi))
    
    @on(Button.Pressed, f"#{BUTTON_DIFF}")
    def action_show_diff(self) -> None:
        """Show diff screen."""
        from app.screens.diff import DiffScreen
        self.push_screen(DiffScreen(self.chezmoi))
    
    @on(Button.Pressed, f"#{BUTTON_EDIT}")
    def action_show_edit(self) -> None:
        """Show edit screen."""
        from app.screens.edit import EditScreen
        self.push_screen(EditScreen(self.chezmoi))
    
    @on(Button.Pressed, f"#{BUTTON_REMOVE}")
    def action_show_remove(self) -> None:
        """Show remove screen."""
        from app.screens.remove import RemoveScreen
        self.push_screen(RemoveScreen(self.chezmoi))
    
    @on(Button.Pressed, f"#{BUTTON_LIST}")
    def action_show_list(self) -> None:
        """Show list screen."""
        from app.screens.list import ListScreen
        self.push_screen(ListScreen(self.chezmoi))


def main():
    """Run the application."""
    app = ChezmoiManager()
    app.run()


if __name__ == "__main__":
    main()
