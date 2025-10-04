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

### Environment Setup
```bash
# Install dependencies with uv
uv sync

# Install dev dependencies
uv sync --dev
```

### Code Quality
```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Running the Application
The application entry point is [main.py](main.py). Once implemented, run with:
```bash
uv run python main.py
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

### Key Features Implemented
1. **Dashboard**: Welcome screen with quick status
2. **Status View**: Detailed chezmoi status (press 's')
3. **File Browser**: DirectoryTree for source directory (press 'f')
4. **Diff Viewer**: Syntax-highlighted diff view (press 'v')
5. **Dark Mode Toggle**: Press 'd' to toggle themes
