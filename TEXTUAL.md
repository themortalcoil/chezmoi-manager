# TEXTUAL.md

Comprehensive documentation about Textual, a Python TUI framework, and how to use it for building the chezmoi-manager application.

## What is Textual?

Textual is a **Rapid Application Development framework for Python** that enables developers to build sophisticated terminal user interfaces (TUIs) using a simple Python API. Applications built with Textual can run in the terminal or web browser.

**Pronunciation:** "teks-choo-uhl" (like "textual")

**License:** MIT (Open Source)

**Created by:** Textualize.io

## Key Features

### Core Capabilities
- **Cross-Platform**: Linux, macOS, Windows support
- **Dual Target**: Terminal and web browser execution
- **Low Resource**: Runs on single-board computers and low-powered devices
- **Remote Friendly**: Works over SSH
- **CLI Integration**: Seamless integration with command-line tools
- **Rich Widget Ecosystem**: 40+ built-in widgets
- **CSS Styling**: Textual CSS for flexible styling
- **Event-Driven**: Reactive programming support
- **Async First**: Native async/await support

### Why Textual for chezmoi-manager?
1. **Subprocess Integration**: Built-in workers for running chezmoi commands
2. **Rich Widgets**: DirectoryTree, DataTable, TextArea perfect for file management
3. **Reactive UI**: Automatic updates when chezmoi state changes
4. **Professional Look**: Modern TUI with colors, animations, and effects
5. **Python Native**: Leverages existing Python ecosystem
6. **Active Development**: Well-maintained with strong community

## Installation

### Requirements
- Python 3.8 or later (we're using 3.13+)
- Terminal with Unicode and color support

### Install Textual
```bash
# Production
pip install textual

# Or with uv (recommended for our project)
uv add textual

# Development tools (optional but recommended)
pip install textual-dev
# or
uv add --dev textual-dev
```

### Optional Extras
```bash
# Syntax highlighting support for TextArea
uv add "textual[syntax]"
```

### Development Tools
```bash
# Run the Textual demo
python -m textual

# Textual console for debugging
textual console

# Run app in development mode
textual run app.py

# Run with console in split view
textual run --dev app.py
```

## Core Concepts

### 1. App Class

Every Textual application starts with a subclass of `App`:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

class ChezmoiManager(App):
    """A TUI for managing chezmoi dotfiles."""

    # CSS styling
    CSS_PATH = "styles.tcss"

    # App metadata
    TITLE = "Chezmoi Manager"
    SUB_TITLE = "Manage your dotfiles"

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app enters application mode."""
        self.title = "Chezmoi Manager"

if __name__ == "__main__":
    app = ChezmoiManager()
    app.run()
```

### 2. Widgets

Widgets are UI components that can be composed together:

```python
def compose(self) -> ComposeResult:
    """Yield widgets to build the UI."""
    yield Header()
    yield DirectoryTree("~/.local/share/chezmoi")
    yield DataTable()
    yield Footer()
```

**Key Pattern**: Use `yield` instead of `return` in `compose()` for better performance.

### 3. Reactivity

Reactive attributes automatically update the UI when changed:

```python
from textual.reactive import reactive

class StatusWidget(Widget):
    """Display chezmoi status."""

    # Reactive attribute - UI updates automatically
    file_count = reactive(0)

    def watch_file_count(self, old_value: int, new_value: int) -> None:
        """Called when file_count changes."""
        self.refresh()

    def render(self) -> str:
        return f"Files managed: {self.file_count}"
```

**Reactive Features:**
- **Smart Refresh**: Auto-updates UI on change
- **Validation**: Validate and modify incoming values
- **Watch Methods**: Trigger actions on change (prefix: `watch_`)
- **Compute Methods**: Calculate derived values with caching (prefix: `compute_`)
- **Data Binding**: Connect parent and child attributes

### 4. Event Handling

Handle events using `on_` prefixed methods:

```python
from textual.widgets import Button

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Click me", id="my-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.notify("Button clicked!")

    def on_key(self, event: events.Key) -> None:
        """Handle key press."""
        if event.key == "q":
            self.exit()
```

**Event Types:**
- Keyboard events: `on_key()`, `key_<name>()`
- Mouse events: `on_click()`, `on_mouse_move()`
- Widget events: `on_button_pressed()`, `on_input_changed()`
- Lifecycle events: `on_mount()`, `on_unmount()`

### 5. Screens

Screens are full-terminal containers for widgets:

```python
from textual.screen import Screen

class DiffScreen(Screen):
    """Screen for viewing file diffs."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield TextArea(id="diff-view")
        yield Footer()

class MainApp(App):
    def on_mount(self) -> None:
        # Push new screen onto stack
        self.push_screen(DiffScreen())

    def action_show_diff(self) -> None:
        """Show diff screen."""
        self.push_screen(DiffScreen())
```

**Screen Navigation:**
- `push_screen(screen)` - Add screen to stack (can go back)
- `pop_screen()` - Remove top screen
- `switch_screen(screen)` - Replace current screen (can't go back)
- `dismiss(result)` - Close screen and return value

**Modal Screens:**
```python
class ConfirmDialog(Screen):
    """Modal confirmation dialog."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }
    """

# Show modal
self.push_screen(ConfirmDialog(), callback=self.on_confirm)
```

### 6. Workers

Workers run background tasks without blocking the UI:

```python
from textual.worker import work

class ChezmoiApp(App):
    @work(exclusive=True, thread=True)
    async def run_chezmoi_status(self) -> str:
        """Run chezmoi status in background."""
        result = subprocess.run(
            ["chezmoi", "status"],
            capture_output=True,
            text=True
        )
        return result.stdout

    def on_button_pressed(self) -> None:
        # Start worker
        worker = self.run_chezmoi_status()
        worker.result_callback = self.on_status_complete

    def on_status_complete(self, result: str) -> None:
        """Called when worker completes."""
        self.query_one(RichLog).write(result)
```

**Worker Features:**
- `@work` decorator for easy creation
- `thread=True` for CPU-bound tasks
- `exclusive=True` to cancel previous workers
- Worker states: PENDING, RUNNING, CANCELLED, ERROR, SUCCESS
- Thread-safe UI updates with `call_from_thread()`

### 7. Actions

Actions are methods that can be triggered by key bindings:

```python
class ChezmoiApp(App):
    # Define key bindings
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "show_diff", "Show Diff"),
        ("a", "apply_changes", "Apply"),
        ("r", "refresh", "Refresh"),
    ]

    def action_show_diff(self) -> None:
        """Show diff screen (triggered by 'd' key)."""
        self.push_screen(DiffScreen())

    def action_apply_changes(self) -> None:
        """Apply chezmoi changes."""
        self.run_worker(self.apply_chezmoi)

    def action_refresh(self) -> None:
        """Refresh status."""
        self.refresh()
```

**Built-in Actions:**
- `action_quit()` - Exit application
- `action_toggle_dark()` - Toggle dark mode
- `action_focus_next()` / `action_focus_previous()` - Navigate focus

### 8. Command Palette

Built-in fuzzy search for commands (Ctrl+P):

```python
class ChezmoiApp(App):
    # Enable command palette (enabled by default)
    ENABLE_COMMAND_PALETTE = True

    # Custom key binding (default is Ctrl+P)
    COMMAND_PALETTE_BINDING = "ctrl+p"

    def get_system_commands(self) -> Iterable[SystemCommand]:
        """Add custom commands to palette."""
        yield SystemCommand(
            "Chezmoi Status",
            "Show status of managed files",
            self.action_show_status
        )
```

## Essential Widgets for chezmoi-manager

### DirectoryTree
Perfect for browsing the chezmoi source directory:

```python
from textual.widgets import DirectoryTree

class FileExplorer(Widget):
    def compose(self) -> ComposeResult:
        yield DirectoryTree("~/.local/share/chezmoi")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection."""
        self.notify(f"Selected: {event.path}")

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """Handle directory selection."""
        self.notify(f"Opened: {event.path}")
```

**Features:**
- Automatic file system traversal
- Filtering with `filter_paths()`
- Events: `FileSelected`, `DirectorySelected`
- Reactive: `show_root`, `show_guides`

### DataTable
Ideal for displaying managed files and status:

```python
from textual.widgets import DataTable

class ManagedFilesTable(Widget):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        # Add columns
        table.add_columns("File", "Status", "Action")

        # Add rows
        table.add_rows([
            (".bashrc", "Modified", "M "),
            (".vimrc", "Added", " A"),
            (".gitconfig", "No change", "  "),
        ])

    def on_data_table_row_selected(
        self, event: DataTable.RowSelected
    ) -> None:
        """Handle row selection."""
        row_key = event.row_key
        self.app.push_screen(DiffScreen(row_key))
```

**Features:**
- Dynamic add/remove rows and columns
- Rich text in cells
- Sorting support
- Cursor navigation (cell, row, column)
- Events: `RowSelected`, `ColumnSelected`, `CellSelected`
- Zebra stripes, fixed rows/columns

### TextArea
For viewing diffs and editing files:

```python
from textual.widgets import TextArea

class DiffViewer(Widget):
    def compose(self) -> ComposeResult:
        # Code editor with syntax highlighting
        yield TextArea.code_editor(
            language="diff",
            theme="monokai"
        )

    def show_diff(self, diff_content: str) -> None:
        """Display diff content."""
        text_area = self.query_one(TextArea)
        text_area.text = diff_content
        text_area.read_only = True
```

**Features:**
- Syntax highlighting (requires `textual[syntax]`)
- Line numbers
- Selection support
- Read-only mode
- Multiple language support
- Programmatic text manipulation

### Input & Forms
For user input and configuration:

```python
from textual.widgets import Input, Button
from textual.containers import Horizontal

class ConfigForm(Widget):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter email", id="email")
        yield Input(placeholder="Enter name", id="name")
        yield Horizontal(
            Button("Save", variant="success"),
            Button("Cancel", variant="error"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.label == "Save":
            email = self.query_one("#email", Input).value
            name = self.query_one("#name", Input).value
            self.save_config(email, name)
```

**Available Input Widgets:**
- `Input` - Single line text
- `TextArea` - Multi-line text
- `Checkbox` - Boolean toggle
- `RadioButton` / `RadioSet` - Mutually exclusive options
- `Select` - Dropdown selection
- `Switch` - On/off toggle

### Other Useful Widgets

**Status & Feedback:**
- `Label` - Static or dynamic text
- `RichLog` - Scrolling log display
- `ProgressBar` - Task progress
- `LoadingIndicator` - Loading spinner
- `Toast` - Temporary notifications

**Navigation:**
- `Tabs` / `TabbedContent` - Tabbed interface
- `Tree` - Hierarchical data
- `ListView` - Scrollable list
- `OptionList` - Selectable options

**Layout:**
- `Header` - App title bar
- `Footer` - Status bar with key bindings
- `Container` - Generic container
- `Horizontal` / `Vertical` - Layout containers

## Styling with Textual CSS

### Basic CSS Structure

Create a `.tcss` file (e.g., `styles.tcss`):

```css
/* Global styles */
Screen {
    background: $surface;
}

/* Widget type selector */
DataTable {
    height: 1fr;
}

/* ID selector */
#status-panel {
    border: solid $primary;
    background: $panel;
    padding: 1;
}

/* Class selector */
.danger {
    background: $error;
    color: $text;
}

/* Pseudo-class */
Button:hover {
    background: $primary;
}

/* Nested selectors */
Container DataTable {
    border: solid blue;
}
```

### Layout Properties

```css
/* Vertical layout (default) */
.container {
    layout: vertical;
    height: 100%;
}

/* Horizontal layout */
.toolbar {
    layout: horizontal;
    height: 3;
}

/* Grid layout */
.dashboard {
    layout: grid;
    grid-size: 2 3;  /* 2 columns, 3 rows */
    grid-gutter: 1;
}

/* Docking */
.header {
    dock: top;
    height: 3;
}

.footer {
    dock: bottom;
    height: 1;
}
```

### Common Properties

```css
/* Sizing */
height: 10;      /* Fixed height */
width: 50%;      /* Percentage */
min-height: 5;
max-width: 80;
height: 1fr;     /* Fraction of remaining space */

/* Spacing */
padding: 1 2;    /* vertical horizontal */
margin: 1;
border: solid blue;
border-title-align: center;

/* Colors */
background: $primary;
color: $text;
border: solid $accent;

/* Display */
display: block;
display: none;
visibility: visible;
visibility: hidden;

/* Positioning */
offset: 5 10;    /* offset-x offset-y */
layer: overlay;
```

### Variables

```css
/* Define variables */
$primary-color: #007acc;
$spacing: 2;

/* Use variables */
Button {
    background: $primary-color;
    padding: $spacing;
}
```

### Loading CSS

```python
# From file
class MyApp(App):
    CSS_PATH = "styles.tcss"

# Inline
class MyApp(App):
    CSS = """
    Screen {
        background: blue;
    }
    """

# Multiple files
class MyApp(App):
    CSS_PATH = ["base.tcss", "components.tcss"]
```

## Application Architecture for chezmoi-manager

### Recommended Project Structure

```
chezmoi-manager/
├── main.py                 # Entry point
├── chezmoi.py             # Chezmoi CLI wrapper
├── app/
│   ├── __init__.py
│   ├── app.py             # Main App class
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── dashboard.py   # Main dashboard screen
│   │   ├── status.py      # Status view screen
│   │   ├── diff.py        # Diff viewer screen
│   │   ├── files.py       # File browser screen
│   │   └── config.py      # Configuration screen
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── status_panel.py
│   │   ├── file_table.py
│   │   ├── diff_viewer.py
│   │   └── command_bar.py
│   └── styles/
│       ├── base.tcss
│       ├── screens.tcss
│       └── widgets.tcss
├── pyproject.toml
└── README.md
```

### Sample App Structure

```python
# app/app.py
from textual.app import App
from .screens.dashboard import DashboardScreen

class ChezmoiManager(App):
    """Main application class."""

    CSS_PATH = "app/styles/base.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("s", "show_status", "Status"),
        ("f", "show_files", "Files"),
        ("ctrl+p", "command_palette", "Commands"),
    ]

    def on_mount(self) -> None:
        """Initialize app."""
        self.push_screen(DashboardScreen())

    def action_show_status(self) -> None:
        """Show status screen."""
        from .screens.status import StatusScreen
        self.push_screen(StatusScreen())
```

### Chezmoi Integration Pattern

```python
# chezmoi.py
import subprocess
import json
from typing import List, Dict, Optional

class ChezmoiWrapper:
    """Wrapper for chezmoi CLI operations."""

    @staticmethod
    def run_command(
        args: List[str],
        format: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Run a chezmoi command."""
        cmd = ["chezmoi"] + args
        if format:
            cmd += ["--format", format]

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

    @classmethod
    def get_status(cls) -> str:
        """Get chezmoi status."""
        result = cls.run_command(["status"])
        return result.stdout

    @classmethod
    def get_managed_files(cls) -> List[str]:
        """Get list of managed files as JSON."""
        result = cls.run_command(["managed"], format="json")
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []

    @classmethod
    def get_diff(cls, target: str = "") -> str:
        """Get diff for target or all files."""
        args = ["diff"]
        if target:
            args.append(target)
        result = cls.run_command(args)
        return result.stdout

    @classmethod
    def apply(cls, dry_run: bool = False) -> str:
        """Apply changes."""
        args = ["apply", "--verbose"]
        if dry_run:
            args.append("--dry-run")
        result = cls.run_command(args)
        return result.stdout

# Usage in widget
from textual.worker import work

class StatusWidget(Widget):
    @work(thread=True)
    async def load_status(self) -> str:
        """Load status in background."""
        return ChezmoiWrapper.get_status()

    def on_mount(self) -> None:
        worker = self.load_status()
        worker.result_callback = self.on_status_loaded

    def on_status_loaded(self, status: str) -> None:
        """Update UI with status."""
        self.query_one(RichLog).write(status)
```

## Best Practices

### 1. Use Composition
Build complex UIs from simple widgets:

```python
class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            StatusPanel(),
            FileTable(),
            id="main-container"
        )
        yield Footer()
```

### 2. Leverage Reactivity
Use reactive attributes for dynamic updates:

```python
class StatusPanel(Widget):
    file_count = reactive(0)
    modified_count = reactive(0)

    def render(self) -> str:
        return f"Files: {self.file_count} | Modified: {self.modified_count}"
```

### 3. Use Workers for Subprocess Calls
Never block the UI with subprocess calls:

```python
@work(thread=True, exclusive=True)
async def run_chezmoi_apply(self) -> str:
    return ChezmoiWrapper.apply()
```

### 4. Organize with Screens
Separate concerns using screens:

```python
# One screen per major view
- DashboardScreen (overview)
- StatusScreen (detailed status)
- DiffScreen (file diffs)
- ConfigScreen (settings)
```

### 5. Handle Errors Gracefully
Always handle subprocess errors:

```python
try:
    result = ChezmoiWrapper.get_status()
    self.update_status(result)
except subprocess.CalledProcessError as e:
    self.notify(f"Error: {e.stderr}", severity="error")
```

### 6. Use IDs and Classes
For querying and styling:

```python
def compose(self) -> ComposeResult:
    yield Button("Apply", id="apply-btn", classes="primary")

# Query by ID
button = self.query_one("#apply-btn", Button)

# Query by class
primary_buttons = self.query(".primary")
```

### 7. Provide Feedback
Always inform users of actions:

```python
def on_button_pressed(self) -> None:
    self.notify("Applying changes...", title="Chezmoi")
    worker = self.run_apply()
    worker.result_callback = lambda result: self.notify(
        "Changes applied!",
        severity="success"
    )
```

## Testing

```python
# tests/test_app.py
from textual.pilot import Pilot
from app.app import ChezmoiManager

async def test_app_loads():
    """Test that app loads successfully."""
    app = ChezmoiManager()
    async with app.run_test() as pilot:
        assert app.title == "Chezmoi Manager"

async def test_status_screen():
    """Test status screen navigation."""
    app = ChezmoiManager()
    async with app.run_test() as pilot:
        # Simulate key press
        await pilot.press("s")
        # Verify screen changed
        assert isinstance(pilot.app.screen, StatusScreen)
```

## Resources

- **Official Documentation**: https://textual.textualize.io/
- **GitHub Repository**: https://github.com/Textualize/textual
- **Discord Community**: https://discord.gg/Enf6Z3qhVr
- **Widget Gallery**: https://textual.textualize.io/widget_gallery/
- **Tutorial**: https://textual.textualize.io/tutorial/
- **Examples**: https://github.com/Textualize/textual/tree/main/examples

## Next Steps for chezmoi-manager

1. **Install Textual**: `uv add textual "textual[syntax]"`
2. **Create basic app structure**: Implement `ChezmoiManager(App)` in `main.py`
3. **Build ChezmoiWrapper**: Implement subprocess wrapper in `chezmoi.py`
4. **Create Dashboard screen**: Status overview with key metrics
5. **Implement File Browser**: Use DirectoryTree for source directory
6. **Add Status View**: DataTable showing file status
7. **Build Diff Viewer**: TextArea for viewing changes
8. **Add Actions**: Implement apply, diff, edit operations
9. **Style the app**: Create `.tcss` files for consistent look
10. **Add error handling**: Graceful degradation when chezmoi not installed
