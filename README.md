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
