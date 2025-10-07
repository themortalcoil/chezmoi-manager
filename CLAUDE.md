# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

chezmoi-manager is a TUI (Terminal User Interface) application for managing chezmoi configurations. The project is in early development with Python files currently empty placeholders.

## Technology Stack

- **Python**: 3.13+ (managed via `.python-version`)
- **Package Manager**: uv (lockfile present)
- **Linting**: Ruff
- **External Dependency**: chezmoi (must be installed separately)

## Development Commands

### Using project.sh (Recommended)
```bash
./project.sh setup    # Install all dependencies
./project.sh run      # Run the application
./project.sh test     # Run unit tests with coverage
./project.sh lint     # Lint and format code
./project.sh clean    # Clean build artifacts
```

### Manual Commands

#### Environment Setup
```bash
# Install dependencies with uv
uv sync

# Install dev dependencies
uv sync --dev

# Install test dependencies
uv sync --group test
```

#### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=. --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_chezmoi.py -v

# Run tests with specific marker
uv run pytest -m unit
```

#### Code Quality
```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .
```

#### Running the Application
```bash
uv run python main.py
# or
./project.sh run
```

## Architecture

### Core Components
- **[main.py](main.py)**: Application entry point for the TUI
- **[chezmoi.py](chezmoi.py)**: Wrapper/interface for chezmoi command-line operations
- **[project.sh](project.sh)**: Project setup and build automation script

### Application Structure
```
app/
├── screens/
│   ├── status.py       # Status screen showing chezmoi status
│   ├── files.py        # File browser with DirectoryTree
│   └── diff.py         # Diff viewer with syntax highlighting
├── widgets/            # Custom widgets (future)
└── styles/
    └── base.tcss       # Base CSS styling
```

### Design Notes
- The application provides an interactive terminal interface for chezmoi operations
- [chezmoi.py](chezmoi.py) handles all interactions with the chezmoi CLI via subprocess
- Workers are used for background tasks to prevent UI blocking
- The project requires bash and chezmoi to be available on the system

### ChezmoiWrapper API

The `ChezmoiWrapper` class in [chezmoi.py](chezmoi.py) provides:

**Core Methods:**
- `check_installed()` - Check if chezmoi is available
- `get_version()` - Get chezmoi version string
- `get_status(targets=None)` - Get status for all or specific files
- `get_managed_files()` - List all managed files
- `get_diff(target="")` - Get diff output
- `apply(targets=None, dry_run=False, verbose=True)` - Apply changes
- `get_data()` - Get template data as dict
- `get_source_dir()` - Get source directory Path
- `doctor()` - Run diagnostics

**Advanced Methods:**
- `verify()` - Verify source state consistency (returns tuple: success, output)
- `add(targets)` - Add files to source state
- `remove(targets)` - Remove files from source state
- `edit(target)` - Get source path for editing
- `update(apply=True)` - Pull from remote repository
- `init(repo="")` - Initialize chezmoi with optional repo

**Error Handling:**
- Raises `ChezmoiNotFoundError` if chezmoi not installed
- Raises `ChezmoiCommandError` with stderr and returncode on failures

### Testing

The project uses pytest for unit testing with the following structure:

```
tests/
├── __init__.py
├── test_chezmoi.py      # ChezmoiWrapper tests (35 tests, 93% coverage)
├── test_widgets.py      # Custom widget tests (8 tests)
└── test_screens.py      # Screen component tests (8 tests)
```

**Test Categories:**
- Unit tests: Isolated component testing with mocks
- Integration tests: Cross-component interactions (planned)
- Coverage target: >80% for core modules

**Running Tests:**
```bash
./project.sh test              # Run all tests with coverage
uv run pytest -m unit          # Run only unit tests
uv run pytest tests/test_chezmoi.py -v  # Run specific file
```

### Key Features Implemented
1. **Add Dotfile**: Add new files to chezmoi with options (press 'a')
2. **Dashboard**: Welcome screen with quick status
3. **Status View**: Detailed chezmoi status (press 's')
4. **File Browser**: DirectoryTree for source directory (press 'f')
5. **Diff Viewer**: Syntax-highlighted diff view with apply (press 'v')
6. **Managed Files**: Table view of all managed files (press 'm')
7. **Template Data**: Tree view of template variables (press 't')
8. **Doctor**: Diagnostic output (press 'c')
9. **Dark Mode Toggle**: Press 'd' to toggle themes
