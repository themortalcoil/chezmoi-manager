# GitHub Copilot Instructions for chezmoi-manager

This file provides guidance to GitHub Copilot when working with code in this repository.

## Project Overview

**chezmoi-manager** is a modern Terminal User Interface (TUI) application for managing [chezmoi](https://www.chezmoi.io/) dotfiles. It provides an interactive, user-friendly interface for common chezmoi operations like viewing status, managing files, viewing diffs, and applying changes.

**Key Features:**
- Status monitoring and file browsing
- Syntax-highlighted diff viewer
- Template data browser
- Diagnostic tools (chezmoi doctor)
- Dark/light mode support
- Keyboard-driven interface

## Technology Stack

- **Language**: Python 3.13+
- **Package Manager**: [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- **TUI Framework**: [Textual](https://textual.textualize.io/) - Modern Python framework for building TUIs
- **Linting/Formatting**: [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter and formatter
- **Testing**: [pytest](https://docs.pytest.org/) with coverage support
- **External Dependency**: [chezmoi](https://www.chezmoi.io/) CLI tool (must be installed separately)

## Project Structure

```
chezmoi-manager/
├── main.py                 # Application entry point - Textual app with navigation
├── chezmoi.py             # Chezmoi CLI wrapper - all subprocess calls to chezmoi
├── project.sh             # Development automation script
├── app/
│   ├── screens/           # Screen implementations (one file per screen)
│   │   ├── status.py      # Status screen - shows chezmoi status output
│   │   ├── files.py       # File browser - DirectoryTree widget
│   │   ├── managed.py     # Managed files table - DataTable widget
│   │   ├── add.py         # Add dotfile screen - form with options
│   │   ├── diff.py        # Diff viewer - syntax highlighted diffs
│   │   ├── data.py        # Template data viewer - tree view
│   │   └── doctor.py      # Diagnostics screen - chezmoi doctor output
│   ├── widgets/           # Custom Textual widgets
│   │   ├── confirm.py     # Confirmation dialog modal
│   │   └── file_input.py  # Enhanced file path input
│   └── styles/
│       └── base.tcss      # Textual CSS styling
├── tests/                 # pytest test suite
│   ├── test_chezmoi.py    # ChezmoiWrapper tests (35 tests, 93% coverage)
│   ├── test_screens.py    # Screen component tests
│   └── test_widgets.py    # Custom widget tests
├── CLAUDE.md              # Claude AI assistant instructions
├── CHEZMOI.md             # Comprehensive chezmoi reference documentation
├── TEXTUAL.md             # Textual framework guide and patterns
└── README.md              # User-facing documentation
```

## Development Workflow

### Setup and Installation

```bash
# First-time setup
./project.sh setup

# Or manually
uv sync
uv sync --dev
uv sync --group test
```

### Running the Application

```bash
./project.sh run
# or
uv run python main.py
```

### Code Quality

**Always run before committing:**

```bash
# Lint and format code (uses Ruff)
./project.sh lint

# Or manually
uv run ruff check .
uv run ruff format .
uv run ruff check --fix .  # Auto-fix issues
```

### Testing

```bash
# Run all tests with coverage
./project.sh test

# Or manually
uv run pytest
uv run pytest --cov=. --cov-report=term-missing
uv run pytest tests/test_chezmoi.py -v  # Specific test file
uv run pytest -m unit                    # Tests with marker
```

**Coverage target:** >80% for core modules

### Build Verification

Before submitting changes:

```bash
./project.sh build  # Runs lint + test
```

## Coding Guidelines

### Python Style

- **Python Version**: 3.13+ features are allowed
- **Formatter**: Ruff (follows PEP 8 with Ruff defaults)
- **Type Hints**: Use type hints where they add clarity
- **Docstrings**: Use for public APIs and complex functions
- **Import Order**: Follow Ruff's isort rules

### Textual/TUI Patterns

1. **Screen Structure**: Each screen is a separate file in `app/screens/`
2. **Composition over Inheritance**: Use `ComposeResult` to yield widgets
3. **Reactive Updates**: Use Textual's reactive system for state changes
4. **Workers**: Use `@work` decorator for background tasks to avoid blocking UI
5. **Bindings**: Define keyboard shortcuts with `BINDINGS` class variable
6. **Styling**: Put styles in the screen's `CSS` class variable or `base.tcss`

Example screen structure:
```python
class MyScreen(Screen):
    CSS = """..."""  # Textual CSS
    BINDINGS = [("escape", "pop_screen", "Back")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield MyWidget()
        yield Footer()
    
    @work(exclusive=True)
    async def my_worker(self) -> None:
        # Background task
        pass
```

### ChezmoiWrapper Usage

- **All chezmoi CLI calls** must go through `ChezmoiWrapper` in `chezmoi.py`
- **Never** modify `~/.local/share/chezmoi` directly
- **Always** handle `ChezmoiCommandError` and `ChezmoiNotFoundError`
- **Use dry-run** when appropriate (destructive operations)
- **Respect user's chezmoi config** (source dir, destination, etc.)

Example:
```python
from chezmoi import ChezmoiWrapper, ChezmoiCommandError

try:
    status = ChezmoiWrapper.status()
    # Process status
except ChezmoiCommandError as e:
    # Handle error with e.stderr and e.returncode
    pass
```

## Important Project Constraints

### chezmoi Integration

1. **State Management**: chezmoi tracks three states:
   - Source state (files in source directory)
   - Target state (after template processing)
   - Destination state (actual files)

2. **File Naming**: Understand chezmoi's special prefixes and suffixes:
   - `dot_` → files starting with `.`
   - `executable_` → executable permissions
   - `private_` → restricted permissions
   - `encrypted_` → encrypted files
   - `.tmpl` → template files

3. **Operations**: Always preview destructive operations with `--dry-run`

4. **Refer to CHEZMOI.md** for comprehensive chezmoi command reference

### UI/UX Principles

- **Keyboard-first**: All operations should have keyboard shortcuts
- **Non-blocking**: Use workers for long-running operations
- **Clear feedback**: Show status, progress, and results clearly
- **Confirmation**: Ask before destructive operations (use ConfirmModal)
- **Help available**: Display key bindings in footer

## Common Tasks

### Adding a New Screen

1. Create new file in `app/screens/`
2. Import in `app/screens/__init__.py`
3. Register in main.py's navigation
4. Add screen-specific tests in `tests/test_screens.py`

### Adding a New ChezmoiWrapper Method

1. Add method to `ChezmoiWrapper` class in `chezmoi.py`
2. Handle errors with `ChezmoiCommandError`
3. Add unit tests in `tests/test_chezmoi.py`
4. Mock subprocess calls in tests

### Updating Dependencies

```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update all dependencies
uv lock --upgrade
```

## Testing Strategy

- **Unit Tests**: Test components in isolation with mocks
- **Mock subprocess**: Use `unittest.mock.patch` for chezmoi CLI calls
- **Screen Tests**: Test screen composition and event handling
- **Widget Tests**: Test custom widget behavior
- **Coverage**: Aim for >80% on core modules (`chezmoi.py`, screens, widgets)

## Documentation References

- **CLAUDE.md** - Additional AI assistant guidance
- **CHEZMOI.md** - Complete chezmoi command reference and concepts
- **TEXTUAL.md** - Textual framework patterns and widget guide
- **README.md** - User-facing documentation
- **IMPROVEMENTS.md** - Recent feature improvements and UX enhancements

## External Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Textual Widget Gallery](https://textual.textualize.io/widget_gallery/)
- [chezmoi Documentation](https://www.chezmoi.io/)
- [chezmoi Command Reference](https://www.chezmoi.io/reference/commands/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [uv Documentation](https://docs.astral.sh/uv/)

## Code Examples

### Typical Screen Pattern

```python
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.worker import work

from chezmoi import ChezmoiWrapper, ChezmoiCommandError

class MyScreen(Screen):
    """Screen for doing something with chezmoi."""
    
    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("r", "refresh", "Refresh"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="content")
        yield Footer()
    
    def on_mount(self) -> None:
        self.load_data()
    
    @work(exclusive=True)
    async def load_data(self) -> None:
        try:
            data = ChezmoiWrapper.some_command()
            self.query_one("#content", Static).update(data)
        except ChezmoiCommandError as e:
            self.query_one("#content", Static).update(
                f"[red]Error:[/red] {e.stderr}"
            )
    
    def action_refresh(self) -> None:
        self.load_data()
```

### Testing Pattern

```python
from unittest.mock import patch, MagicMock
import pytest
from chezmoi import ChezmoiWrapper, ChezmoiCommandError

def test_status_success():
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "status output"
    
    with patch("subprocess.run", return_value=mock_result):
        result = ChezmoiWrapper.status()
        assert result == "status output"

def test_status_error():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "error message"
    
    with patch("subprocess.run", return_value=mock_result):
        with pytest.raises(ChezmoiCommandError):
            ChezmoiWrapper.status()
```

## Contributing

When contributing:

1. **Follow existing patterns** in the codebase
2. **Run `./project.sh lint`** before committing
3. **Run `./project.sh build`** to verify quality
4. **Add tests** for new functionality
5. **Update documentation** if adding features or changing APIs
6. **Keep changes focused** - one feature/fix per PR

## Notes for AI Assistants

- This is a **TUI application**, not a web app or CLI tool
- The app **wraps chezmoi**, it doesn't replace it
- Users are expected to have **chezmoi already installed and configured**
- The codebase uses **modern Python 3.13+ features**
- **Textual** is the only acceptable TUI framework for this project
- All UI changes should be **keyboard-accessible**
- Reference **CHEZMOI.md** and **TEXTUAL.md** for domain-specific guidance
