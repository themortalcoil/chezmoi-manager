"""Template data viewer screen."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, Tree
from textual.widgets.tree import TreeNode
from textual.worker import Worker, WorkerState

from chezmoi import ChezmoiWrapper


class TemplateDataScreen(Screen):
    """Screen for viewing template data."""

    CSS = """
    TemplateDataScreen {
        align: center top;
    }

    #data-container {
        width: 95%;
        height: 1fr;
        background: $panel;
        border: solid $primary;
        padding: 1 2;
        margin: 1;
    }

    #data-title {
        padding: 1 0;
        text-style: bold;
    }

    Tree {
        height: 1fr;
        scrollbar-gutter: stable;
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
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Vertical(id="data-container"):
            yield Static("[bold]Template Data[/bold]", id="data-title")
            yield Static(
                "[dim]Loading template data...[/dim]", classes="loading", id="loading"
            )
            yield Tree("Template Data", id="data-tree")

        with Vertical(id="actions-container"):
            yield Button("Refresh", variant="primary", id="btn-refresh")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.title = "Template Data"
        self.sub_title = "Press 'r' to refresh, 'esc' to go back"

        # Hide tree initially
        tree = self.query_one("#data-tree", Tree)
        tree.display = False

        # Load data
        self.load_data()

    def load_data(self) -> None:
        """Load template data in background worker."""
        self.run_worker(self._fetch_data, exclusive=True, thread=True)

    async def _fetch_data(self) -> dict:
        """Fetch template data from chezmoi."""
        try:
            return ChezmoiWrapper.get_data()
        except Exception as e:
            self.app.notify(f"Error loading data: {e}", severity="error")
            return {}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result is not None:
                self.update_tree(event.worker.result)

    def update_tree(self, data: dict) -> None:
        """Update tree with template data."""
        # Hide loading message
        loading = self.query_one("#loading", Static)
        loading.display = False

        # Show and populate tree
        tree = self.query_one("#data-tree", Tree)
        tree.display = True
        tree.clear()
        tree.show_root = True

        if not data:
            tree.label = "[yellow]No template data available[/yellow]"
            return

        tree.label = "[bold cyan]Template Data[/bold cyan]"

        # Build tree from data
        self._add_dict_to_tree(tree.root, data)

        tree.root.expand()

    def _add_dict_to_tree(self, node: TreeNode, data: dict) -> None:
        """Recursively add dictionary data to tree."""
        for key, value in data.items():
            if isinstance(value, dict):
                # Add as expandable node
                child = node.add(f"[cyan]{key}[/cyan]", expand=False)
                self._add_dict_to_tree(child, value)
            elif isinstance(value, list):
                # Add list
                child = node.add(f"[yellow]{key}[/yellow] ({len(value)} items)")
                for idx, item in enumerate(value):
                    if isinstance(item, (dict, list)):
                        item_node = child.add(f"[dim]{idx}[/dim]")
                        if isinstance(item, dict):
                            self._add_dict_to_tree(item_node, item)
                        else:
                            item_node.add_leaf(str(item))
                    else:
                        child.add_leaf(f"{idx}: {item}")
            elif isinstance(value, bool):
                # Boolean value
                node.add_leaf(f"[green]{key}[/green] = [magenta]{value}[/magenta]")
            elif isinstance(value, (int, float)):
                # Numeric value
                node.add_leaf(f"[green]{key}[/green] = [blue]{value}[/blue]")
            elif value is None:
                # Null value
                node.add_leaf(f"[green]{key}[/green] = [dim]null[/dim]")
            else:
                # String value
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                node.add_leaf(f"[green]{key}[/green] = {value_str}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-refresh":
            self.action_refresh()

    def action_refresh(self) -> None:
        """Refresh the data tree."""
        # Show loading
        loading = self.query_one("#loading", Static)
        loading.display = True

        tree = self.query_one("#data-tree", Tree)
        tree.display = False

        self.load_data()
        self.app.notify("Refreshing template data...", timeout=1)

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
