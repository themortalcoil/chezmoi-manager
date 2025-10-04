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

### Design Notes
- The application will provide an interactive terminal interface for chezmoi operations
- [chezmoi.py](chezmoi.py) should handle all interactions with the chezmoi CLI
- The project requires bash and chezmoi to be available on the system
