
# chezmoi-manager

A beautiful TUI (Terminal User Interface) for managing your chezmoi dotfiles with ease.

## Features

### ✨ Enhanced File Addition
- **Common Files Quick Selection** - Click to select from frequently used config files
- **File Conflict Detection** - Prevents adding already managed files
- **Live Preview Panel** - See exactly what will happen before you commit
- **Browse Files Button** - Visual file picker for easy selection
- **Quick Presets** - One-click configurations for common scenarios (Private, Template, Executable, Readonly)
- **Advanced Options** - Fine-grained control over file attributes
- **Enhanced Feedback** - Detailed success messages with next steps

### 🔍 Professional Diff Viewer
- **Syntax Highlighting** - Beautiful Monokai theme with line numbers
- **File Selector Panel** - Click files to view individual diffs
- **Statistics Panel** - Real-time metrics (files, additions, deletions, net change)
- **Split View** - Sidebar with stats and file list
- **Export Features** - Save diffs as `.patch` files
- **Selective Apply** - Apply all or specific file changes
- **Comprehensive Error Handling** - Bulletproof error recovery

### 🎨 Vertical UI Layout
- Clean vertical button layout for better usability
- Consistent spacing and alignment
- Responsive design that adapts to terminal size

## Installation

```bash
# Clone the repository
git clone https://github.com/themortalcoil/chezmoi-manager.git
cd chezmoi-manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Requirements

- Python 3.10+
- chezmoi installed and initialized
- textual >= 0.40.0
- rich >= 13.0.0

## Usage

### Main Menu

The main menu provides five core operations:

1. **📝 Add File** - Add a new file to chezmoi
2. **🔍 View Diff** - View and apply changes
3. **✏️ Edit File** - Edit managed files (coming soon)
4. **🗑️ Remove File** - Remove files from chezmoi
5. **📋 List Files** - View all managed files

### Add File Workflow

1. Enter file path or click "Browse Files"
2. Select from common dotfiles if desired
3. Choose a quick preset or configure advanced options
4. Review the live preview
5. Click "Add File"

### View Diff Workflow

1. View statistics and changed files in the sidebar
2. Click a file to see its specific diff
3. Use keyboard shortcuts:
   - `n` - Next change (planned)
   - `p` - Previous change (planned)
   - `escape` - Back to main menu
4. Click "Apply All" to apply changes
5. Click "Export" to save diff as a patch file

## Architecture

### Refactoring Improvements Implemented

Following best practices and code analysis, the following refactoring improvements were implemented:

#### 1. **Base Screen Class** (`app/base_screen.py`)
- Eliminates duplicate code across all screens
- Common bindings and methods inherited by all screens
- Reduces ~70 lines of duplicate code

#### 2. **Constants Module** (`app/constants.py`)
- Centralizes all magic strings and values
- Makes the codebase easier to maintain
- Single source of truth for configuration

#### 3. **Package Exports** (`__init__.py` files)
- Clear public API definitions
- Better module organization
- Easier imports for consumers

# Chezmoi Manager

A modern Terminal User Interface (TUI) application for managing [chezmoi](https://www.chezmoi.io/) dotfiles with ease.

![Chezmoi Manager](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.13+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

✨ **Core Functionality:**
- 📊 **Status View** - Real-time chezmoi status monitoring
- 📁 **File Browser** - Navigate your source directory with DirectoryTree
- 📝 **Managed Files Table** - View all managed files in a searchable table
- 🔍 **Diff Viewer** - Syntax-highlighted diff viewing
- ✅ **Apply Changes** - Apply changes with confirmation dialog
- 📋 **Template Data** - Browse template variables in a tree view
- 🏥 **Doctor Diagnostics** - Run chezmoi doctor for system checks

🎨 **User Experience:**
- Dark/Light mode toggle
- Keyboard shortcuts for all actions
- Background workers for non-blocking operations
- Smooth screen navigation
- Rich text formatting and colors

## Requirements

- **Python**: 3.13 or higher
- **chezmoi**: Installed and configured ([install guide](https://www.chezmoi.io/install/))
- **uv**: Python package manager ([install guide](https://docs.astral.sh/uv/))

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/chezmoi-manager.git
cd chezmoi-manager

# Setup and run
./project.sh setup
./project.sh run
```

## Installation

### Using project.sh (Recommended)

```bash
# First-time setup
./project.sh setup

# Run the application
./project.sh run

# Other commands
./project.sh lint    # Lint and format code
./project.sh build   # Run code quality checks
./project.sh clean   # Remove cache files
```

### Manual Installation

```bash
# Install dependencies
uv sync

# Run the application
uv run python main.py
```

## Usage

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `s` | Show Status screen |
| `f` | Show File Browser |
| `m` | Show Managed Files table |
| `v` | Show Diff Viewer |
| `t` | Show Template Data |
| `c` | Run Doctor diagnostics |
| `d` | Toggle Dark/Light mode |
| `q` | Quit application |
| `Esc` | Go back / Close screen |
| `Ctrl+P` | Command palette |

### Screens

**Dashboard**
- Welcome message
- Quick status overview
- Navigation buttons

**Status (s)**
- Detailed chezmoi status output
- Shows pending changes
- Refresh with `r`

**File Browser (f)**
- Navigate source directory
- View file information
- See target paths

**Managed Files (m)**
- Table view of all managed files
- File count statistics
- Row selection

**Diff Viewer (v)**
- Syntax-highlighted diffs
- Apply changes with confirmation
- Refresh capability

**Template Data (t)**
- Browse all template variables
- Tree structure view
- Expandable nodes

**Doctor (c)**
- Run system diagnostics
- Colorized output
- Health check status

## Development


### Project Structure

```
chezmoi-manager/
├── app/
│   ├── __init__.py           # Package exports
│   ├── base_screen.py        # Base class for all screens
│   ├── constants.py          # Application constants
│   ├── chezmoi_wrapper.py    # Core chezmoi CLI wrapper
│   ├── screens/              # UI screens
│   │   ├── __init__.py       # Screen exports
│   │   ├── add.py            # Add file screen
│   │   ├── diff.py           # Diff viewer screen
│   │   ├── edit.py           # Edit screen (planned)
│   │   ├── remove.py         # Remove file screen
│   │   ├── list.py           # List managed files screen
│   │   └── browse.py         # File browser screen
│   └── widgets/              # Custom widgets
│       └── __init__.py       # FileInput, OptionsPanel, ResultPanel, PreviewPanel
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_chezmoi_wrapper.py  # ChezmoiWrapper tests (35 tests)
│   └── test_screens.py       # Screen & widget tests
├── main.py                   # Application entry point
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── setup.py                  # Package setup
└── README.md                 # This file
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

### Code Quality

The codebase follows these principles:

- **DRY (Don't Repeat Yourself)** - Base classes and constants eliminate duplication
- **Single Responsibility** - Each module has a clear, focused purpose
- **Comprehensive Error Handling** - All operations handle errors gracefully
- **Type Hints** - Python type annotations throughout
- **Documentation** - Docstrings for all public APIs

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) - amazing TUI framework
- Powered by [chezmoi](https://www.chezmoi.io/) - dotfile manager
- Syntax highlighting by [Rich](https://rich.readthedocs.io/)
├── main.py                 # Application entry point
├── chezmoi.py             # Chezmoi CLI wrapper
├── project.sh             # Development automation
├── app/
│   ├── screens/           # Screen implementations
│   │   ├── status.py      # Status screen
│   │   ├── files.py       # File browser
│   │   ├── managed.py     # Managed files table
│   │   ├── diff.py        # Diff viewer
│   │   ├── data.py        # Template data viewer
│   │   └── doctor.py      # Diagnostics screen
│   ├── widgets/           # Custom widgets
│   │   └── confirm.py     # Confirmation dialog
│   └── styles/            # CSS styling
│       └── base.tcss      # Base styles
├── CLAUDE.md              # AI assistant instructions
├── CHEZMOI.md             # Chezmoi documentation
└── TEXTUAL.md             # Textual framework guide
```

### Technology Stack

- **[Textual](https://textual.textualize.io/)** - Modern TUI framework
- **[Python 3.13](https://www.python.org/)** - Programming language
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **[Ruff](https://docs.astral.sh/ruff/)** - Linter and formatter
- **[tree-sitter](https://tree-sitter.github.io/)** - Syntax highlighting

### Code Quality

```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Auto-fix and format
./project.sh lint
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `./project.sh lint` to format code
5. Run `./project.sh build` to verify quality
6. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [chezmoi](https://www.chezmoi.io/) - Excellent dotfile manager by Tom Payne
- [Textual](https://textual.textualize.io/) - Amazing TUI framework by Textualize
- Built with ❤️ using Python and modern tooling

## Support

- 📖 [Documentation](CHEZMOI.md) - Chezmoi integration guide
- 📚 [Textual Guide](TEXTUAL.md) - TUI development reference
- 🐛 [Issues](https://github.com/yourusername/chezmoi-manager/issues) - Report bugs
- 💬 [Discussions](https://github.com/yourusername/chezmoi-manager/discussions) - Ask questions
