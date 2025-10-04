This is a comprehensive project plan and architecture for creating a TUI wrapper for `chezmoi`, utilizing Python and Textualize for the interface, and managed via a robust shell script.

### Project Overview

**Working Title:** `LazyMoi`
**Goal:** To provide an intuitive, dashboard-like TUI (similar to `lazygit` or `lazydocker`) for visualizing `chezmoi` status, reviewing diffs, applying changes, editing source files, and managing the source Git repository.

### Architecture

The architecture is designed around responsiveness and separation of concerns. The UI must remain responsive while potentially long-running `chezmoi` commands execute in the background.

#### 1\. Core Components

1. **UI Layer (Textual/Rich):** Handles rendering, user input (keybindings), and visualization. Composed of custom widgets (FileStatusList, DiffViewer, StatusBar).
2. **Application State Manager (Python):** Manages the current view, the list of modified files, and the currently selected item.
3. **Chezmoi Driver (Python Backend):** A dedicated module responsible for interacting with the `chezmoi` binary. This is the most critical component for performance.
      * It must use `asyncio.create_subprocess_exec` to run commands asynchronously.
      * It should prioritize parsing structured output (e.g., `chezmoi status --format json`) for reliability.
4. **Management Script (`run.sh`):** Handles environment setup, dependency management, and execution.

#### 2\. Project Structure

```
lazymoi/
│
├── run.sh                  # Project management script (Setup, Run, Test, Clean)
├── pyproject.toml          # Python dependencies (Textual) and metadata
│
└── src/
    └── lazymoi/
        ├── __main__.py     # Application entry point
        ├── app.py          # Main Textual application class and bindings
        ├── driver.py       # Backend interaction with the chezmoi binary
        ├── models.py       # Data models (e.g., ManagedFileStatus)
        │
        └── widgets/
            ├── file_list.py    # Widget for listing file status (Modified/Added/Deleted)
            ├── diff_viewer.py  # Widget for displaying syntax-highlighted diffs
            └── modals.py       # Modal screens (e.g., CommitMessage, ConfirmAction)
```

#### 3\. Data Flow

1. **Startup:** `run.sh` prepares the environment and starts the Textual App (`app.py`).
2. **Initial Load:** The App initializes the `ChezmoiDriver` and asynchronously calls `driver.get_status()`.
3. **Render Status:** The results are parsed into models and passed to the `FileList` widget.
4. **User Interaction:** The user navigates the list.
5. **Fetch Diff:** The App catches the selection event and asynchronously calls `driver.get_diff(selected_file)`.
6. **Update UI:** The resulting diff is passed to the `DiffViewer` widget, which uses Rich's `Syntax` class to render the highlighted output.
7. **Action Execution:** The user presses a key (e.g., 'A' for Apply). The App calls `driver.apply(selected_file)`.
8. **Refresh:** After the action completes, the App refreshes the status (back to step 2).

### The Management Script (`run.sh`)

This script provides a unified interface for the development lifecycle.

```bash
#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

VENV_DIR=".venv"
# The entry point for the application execution
APP_MODULE="src.lazymoi.__main__"

# Function to activate the virtual environment
activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Virtual environment not found. Please run './run.sh setup' first."
        exit 1
    fi
    source "$VENV_DIR/bin/activate"
}

case "$1" in
    setup)
        echo "--- Setting up the development environment ---"
        if ! command -v python3 &> /dev/null; then
            echo "Error: python3 is not installed."
            exit 1
        fi

        # Create virtual environment
        [ ! -d "$VENV_DIR" ] && python3 -m venv $VENV_DIR
        activate_venv

        echo "Installing/Updating Python dependencies..."
        pip install -U pip
        # Install dependencies from pyproject.toml (assuming 'dev' extras are defined)
        pip install ".[dev]"
        # Install textual-dev for debugging tools
        pip install textual-dev

        echo "Setup complete. Use './run.sh start' to run the application."
        ;;

    start)
        activate_venv

        # Check for external dependency
        if ! command -v chezmoi &> /dev/null; then
            echo "Error: chezmoi binary not found in PATH."
            echo "Please install chezmoi (https://www.chezmoi.io/install/) and try again."
            exit 1
        fi

        echo "--- Starting LazyMoi (Development Mode with Hot Reloading) ---"
        # Use 'textual run --dev' for a better development experience
        textual run --dev $APP_MODULE
        ;;

    test)
        echo "--- Running tests ---"
        activate_venv
        pytest
        ;;

    format)
        echo "--- Formatting code (Black/isort) ---"
        activate_venv
        black src tests
        isort src
        ;;

    console)
        # Useful for debugging Textual layouts using the dev console
        activate_venv
        textual console
        ;;

    clean)
        echo "--- Cleaning up environment and cache ---"
        rm -rf $VENV_DIR
        find . -type d -name "__pycache__" -exec rm -r {} +
        echo "Clean complete."
        ;;

    *)
        echo "Usage: $0 {setup|start|test|format|console|clean}"
        exit 1
        ;;
esac
```

### Development Plan (Phased Approach)

#### Phase 1: Foundation and Core Integration (Est. 3 Days)

1. **Project Setup:** Initialize the repository, create the directory structure, `pyproject.toml`, and implement the `run.sh` script.
2. **Textual Skeleton:** Create the basic Textual application structure (`app.py`) with a main layout (Header, Footer, Sidebar area, Main Content area).
3. **Chezmoi Driver (Async):** Implement `driver.py`. Focus on the asynchronous `run_command` function using `asyncio.create_subprocess_exec`.
4. **Status Parsing:** Implement `driver.get_status()`. Utilize `chezmoi status --format json` (or similar structured output) and parse it into the `ManagedFileStatus` models.
5. **Basic Display:** Display the parsed status in a `DataTable` or `ListView` widget in the sidebar.

#### Phase 2: Visualization and Core Actions (Est. 4 Days)

1. **Diff Viewer Widget:** Implement `diff_viewer.py`. When a file is selected in the sidebar, asynchronously fetch the diff.
2. **Syntax Highlighting:** Utilize Rich's `Syntax` class within the `DiffViewer` to highlight the diff output effectively.
3. **Keybindings:** Define core keybindings (Quit, Refresh, Apply, Edit).
4. **Implementing 'Apply':** Implement the workflow for `chezmoi apply <target>`. Use a modal for confirmation if applying all changes.
5. **Implementing 'Edit':** Implement the workflow for `chezmoi edit <target>`. This requires the TUI to temporarily suspend or manage the execution of the user's external `$EDITOR`.
6. **State Refresh:** Ensure the UI (file list and diff viewer) automatically refreshes after any action is completed.

#### Phase 3: Advanced Workflows and Git Integration (Est. 3 Days)

1. **Git Actions:** Implement Git workflows for the source repository.
2. **Commit Modal:** Create a `CommitMessage` modal screen. Upon submission, the driver should execute `git add .`, `git commit -m <message>`, and `git push` within the chezmoi source directory.
3. **Update Workflow:** Implement functionality to run `chezmoi update` (pulling from remote and updating externals).
4. **Data View:** Add a secondary screen to view the output of `chezmoi data` (template variables).

#### Phase 4: Polish and Distribution (Est. 2 Days)

1. **Error Handling:** Robustly handle errors from the `chezmoi` binary (e.g., merge conflicts, missing password manager) and display them clearly using Textual Toasts or Modals.
2. **Styling:** Use Textual CSS (TCSS) to refine the layout and appearance.
3. **Help Modal:** Add a modal screen displaying all available keybindings.
4. **Packaging:** Finalize `pyproject.toml` for distribution via PyPI (allowing installation via `pipx`).
