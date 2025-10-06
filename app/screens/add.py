"""Screen for adding dotfiles to chezmoi."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListView,
    ListItem,
    Static,
)
from textual.worker import Worker, WorkerState

from app.widgets.file_input import FileInput
from chezmoi import ChezmoiCommandError, ChezmoiWrapper


# File patterns that typically use templates
TEMPLATE_PATTERNS = {
    ".gitconfig",
    ".ssh/config",
    ".config/git/config",
}

# File patterns that should be encrypted
ENCRYPT_PATTERNS = {
    ".ssh/id_rsa",
    ".ssh/id_ed25519",
    ".gnupg",
    ".aws/credentials",
    ".netrc",
}

# Common config files
COMMON_DOTFILES = [
    "~/.bashrc",
    "~/.zshrc",
    "~/.vimrc",
    "~/.gitconfig",
    "~/.tmux.conf",
    "~/.config/nvim/init.vim",
    "~/.ssh/config",
]


class CommonFilesPanel(Static):
    """Panel showing common dotfiles for quick selection."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Common Dotfiles[/bold]")
        yield Label("[dim]Click to auto-fill path[/dim]")
        with ListView(id="common-files-list"):
            for idx, file_path in enumerate(COMMON_DOTFILES):
                item = ListItem(Label(file_path), classes="common-file-item")
                item.file_path = file_path  # Store as custom attribute
                yield item


class QuickPresets(Static):
    """Panel for quick preset buttons."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Quick Presets[/bold]")
        yield Label("[dim]Click to auto-configure options[/dim]")
        with Horizontal():
            yield Button("🔧 Basic File", variant="success", id="preset-basic")
            yield Button("📝 Template", variant="primary", id="preset-template")
            yield Button("🔒 Encrypted", variant="warning", id="preset-encrypt")
            yield Button("📁 Directory", variant="default", id="preset-directory")


class OptionsPanel(Static):
    """Panel for add command options."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Advanced Options[/bold]", id="options-title")
        yield Label("[dim]Auto-configured based on file type[/dim]")
        yield Checkbox("Template - Use variables like {{ .email }}", id="opt-template")
        yield Checkbox("Encrypt - Encrypt with age/gpg", id="opt-encrypt")
        yield Checkbox(
            "Recursive - Include subdirectories", id="opt-recursive", value=True
        )
        yield Checkbox("Exact - Remove unmanaged files from directory", id="opt-exact")
        yield Checkbox(
            "Autotemplate - Auto-detect template variables", id="opt-autotemplate"
        )
        yield Checkbox("Follow - Add symlink target", id="opt-follow")
        yield Checkbox("Create - Track file existence only", id="opt-create")


class ResultPanel(Static):
    """Panel for displaying results."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Result[/bold]", id="result-title")
        yield Label("")
        yield Label("[dim]Ready to add files...[/dim]", id="result-content")

    def update_result(self, message: str, success: bool = True) -> None:
        """Update result display.

        Args:
            message: Message to display.
            success: Whether operation was successful.
        """
        color = "green" if success else "red"
        self.query_one("#result-content", Label).update(f"[{color}]{message}[/{color}]")

    def update_working(self, message: str) -> None:
        """Update with working status.

        Args:
            message: Status message.
        """
        self.query_one("#result-content", Label).update(f"[yellow]{message}[/yellow]")


class PreviewPanel(Static):
    """Panel for previewing what will be added."""

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("[bold]Preview[/bold]", id="preview-title")
        yield Label("[dim]Shows what will happen when you click Add[/dim]")
        yield Label("", id="preview-content")

    def update_preview(self, file_path: str, options: dict[str, bool]) -> None:
        """Update preview with current settings.

        Args:
            file_path: File path to add.
            options: Options that will be applied.
        """
        if not file_path:
            self.query_one("#preview-content", Label).update(
                "[dim]Enter a file path to see preview[/dim]"
            )
            return

        # Build preview text
        preview_lines = [f"[cyan]File:[/cyan] {file_path}"]

        # Try to get source path
        try:
            from pathlib import Path

            expanded_path = str(Path(file_path).expanduser())
            source_path = ChezmoiWrapper.get_source_path(expanded_path)
            preview_lines.append(f"[cyan]Source:[/cyan] {source_path}")
        except Exception:
            preview_lines.append(
                "[yellow]Source: Will be determined during add[/yellow]"
            )

        # Show enabled options
        enabled_opts = [opt for opt, enabled in options.items() if enabled]
        if enabled_opts:
            preview_lines.append(f"[cyan]Options:[/cyan] {', '.join(enabled_opts)}")
        else:
            preview_lines.append("[cyan]Options:[/cyan] [dim]none[/dim]")

        # Add helpful hints
        if options.get("template"):
            preview_lines.append(
                "[dim]💡 Template variables like {{ .email }} will be supported[/dim]"
            )
        if options.get("encrypt"):
            preview_lines.append("[dim]🔒 File will be encrypted in source state[/dim]")
        if options.get("exact"):
            preview_lines.append(
                "[dim]⚠️  Exact mode: unmanaged files in directory will be removed on apply[/dim]"
            )

        self.query_one("#preview-content", Label).update("\n".join(preview_lines))


class AddDotfileScreen(Screen):
    """Screen for adding dotfiles to chezmoi."""

    CSS = """
    AddDotfileScreen {
        align: center top;
    }

    #add-container {
        width: 90%;
        height: auto;
        background: $panel;
        border: solid $primary;
        padding: 2 4;
        margin: 2;
    }

    #file-input-container {
        width: 100%;
        height: auto;
        padding: 1 0;
    }

    FileInput {
        width: 100%;
        height: auto;
    }

    FileInput Horizontal {
        width: 100%;
        height: auto;
    }

    FileInput Input {
        width: 1fr;
    }

    FileInput #validation-status {
        width: auto;
        margin-left: 1;
    }

    #browse-button {
        margin-top: 1;
        width: 100%;
    }

    CommonFilesPanel {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin-top: 1;
        border: solid $success;
        max-height: 12;
    }

    CommonFilesPanel ListView {
        height: 8;
        border: none;
    }

    .common-file-item {
        height: 1;
    }

    QuickPresets {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin-top: 1;
        border: solid $primary;
    }

    QuickPresets Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
    }

    QuickPresets Button {
        margin: 0 1;
        min-width: 16;
    }

    OptionsPanel {
        width: 100%;
        height: auto;
        padding: 1 0;
        margin-top: 1;
        border: solid $accent;
        padding: 1 2;
    }

    PreviewPanel {
        width: 100%;
        height: auto;
        padding: 1 0;
        margin-top: 1;
        border: solid $warning;
        padding: 1 2;
    }

    ResultPanel {
        width: 100%;
        height: auto;
        padding: 1 0;
        margin-top: 1;
        border: solid $success;
        padding: 1 2;
    }

    #actions-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
        margin-top: 1;
    }

    #actions-container Button {
        margin: 0 1;
        min-width: 14;
    }
    """

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("ctrl+a", "add_file", "Add File"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()

        with Vertical(id="add-container"):
            yield Label("[bold cyan]Add Dotfile to chezmoi[/bold cyan]")
            yield Label("")
            yield Label("Enter the path to the file or directory you want to manage:")

            with Vertical(id="file-input-container"):
                yield FileInput(
                    placeholder="~/path/to/file or select from common files below"
                )
                yield Button("📁 Browse Files", variant="default", id="browse-button")

            yield CommonFilesPanel()
            yield QuickPresets()
            yield OptionsPanel()
            yield PreviewPanel()
            yield ResultPanel()

        with Horizontal(id="actions-container"):
            yield Button("Add File", variant="primary", id="btn-add")
            yield Button("Back", variant="default", id="btn-back")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen."""
        self.sub_title = "Press Ctrl+A to add file, Esc to go back"
        # Set up file input listener for smart defaults
        file_input = self.query_one(FileInput)
        file_input.watch(file_input, "file_path", self._apply_smart_defaults)

        # Update preview initially
        self._update_preview()

    def _update_preview(self) -> None:
        """Update the preview panel with current state."""
        file_input = self.query_one(FileInput)
        file_path = file_input.file_path.strip()

        if not file_path:
            preview_panel = self.query_one(PreviewPanel)
            preview_panel.update_preview("", {})
            return

        options = {
            "template": self.query_one("#opt-template", Checkbox).value,
            "encrypt": self.query_one("#opt-encrypt", Checkbox).value,
            "recursive": self.query_one("#opt-recursive", Checkbox).value,
            "exact": self.query_one("#opt-exact", Checkbox).value,
            "autotemplate": self.query_one("#opt-autotemplate", Checkbox).value,
            "follow": self.query_one("#opt-follow", Checkbox).value,
            "create": self.query_one("#opt-create", Checkbox).value,
        }

        preview_panel = self.query_one(PreviewPanel)
        preview_panel.update_preview(file_path, options)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes to update preview."""
        self._update_preview()

    def _apply_smart_defaults(self, file_path: str) -> None:
        """Apply smart defaults based on file path.

        Args:
            file_path: The file path entered by user.
        """
        if not file_path:
            return

        # Check for template patterns
        should_template = any(pattern in file_path for pattern in TEMPLATE_PATTERNS)
        if should_template:
            self.query_one("#opt-template", Checkbox).value = True

        # Check for encrypt patterns
        should_encrypt = any(pattern in file_path for pattern in ENCRYPT_PATTERNS)
        if should_encrypt:
            self.query_one("#opt-encrypt", Checkbox).value = True

        # Check if it's a directory
        file_input = self.query_one(FileInput)
        if file_input.is_valid and file_input.get_path_obj().is_dir():
            # For directories, suggest recursive
            self.query_one("#opt-recursive", Checkbox).value = True

        # Update preview after applying defaults
        self._update_preview()

    def _apply_preset(self, preset: str) -> None:
        """Apply a quick preset configuration.

        Args:
            preset: Preset name (basic, template, encrypt, directory).
        """
        # Reset all checkboxes first
        self.query_one("#opt-template", Checkbox).value = False
        self.query_one("#opt-encrypt", Checkbox).value = False
        self.query_one("#opt-recursive", Checkbox).value = True
        self.query_one("#opt-exact", Checkbox).value = False
        self.query_one("#opt-autotemplate", Checkbox).value = False
        self.query_one("#opt-follow", Checkbox).value = False
        self.query_one("#opt-create", Checkbox).value = False

        if preset == "basic":
            # Basic file - defaults are fine
            pass
        elif preset == "template":
            self.query_one("#opt-template", Checkbox).value = True
            self.query_one("#opt-autotemplate", Checkbox).value = True
        elif preset == "encrypt":
            self.query_one("#opt-encrypt", Checkbox).value = True
        elif preset == "directory":
            self.query_one("#opt-recursive", Checkbox).value = True
            self.query_one("#opt-exact", Checkbox).value = True

        # Show notification
        preset_names = {
            "basic": "Basic File",
            "template": "Template File",
            "encrypt": "Encrypted File",
            "directory": "Exact Directory",
        }
        self.app.notify(
            f"Applied {preset_names.get(preset, preset)} preset",
            title="Preset Applied",
            severity="information",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "btn-back":
            self.app.pop_screen()
        elif button_id == "btn-add":
            self.action_add_file()
        elif button_id == "browse-button":
            # Push file browser screen
            from app.screens.files import FileBrowserScreen

            self.app.push_screen(FileBrowserScreen(), self._handle_file_selected)
        elif button_id.startswith("preset-"):
            preset_name = button_id.replace("preset-", "")
            self._apply_preset(preset_name)

    def _handle_file_selected(self, file_path: str | None) -> None:
        """Handle file selection from file browser.

        Args:
            file_path: Selected file path or None if cancelled.
        """
        if file_path:
            file_input = self.query_one(FileInput)
            input_widget = file_input.query_one(Input)
            input_widget.value = file_path
            input_widget.focus()

            self.app.notify(
                f"Selected: {file_path}",
                title="File Selected",
                severity="information",
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from common files list."""
        # Get the file path from the selected list item's custom attribute
        if event.item and hasattr(event.item, "file_path"):
            file_path = event.item.file_path

            # Set the file path in the input
            file_input = self.query_one(FileInput)
            input_widget = file_input.query_one(Input)
            input_widget.value = str(file_path)

            # Focus the input so user can see/edit
            input_widget.focus()

            self.app.notify(
                f"Selected: {file_path}",
                title="File Selected",
                severity="information",
            )

    def action_add_file(self) -> None:
        """Add the file to chezmoi."""
        file_input = self.query_one(FileInput)

        # Validate input
        if not file_input.is_valid:
            result_panel = self.query_one(ResultPanel)
            result_panel.update_result("Please enter a valid file path", success=False)
            return

        # Get file path
        file_path = file_input.get_path()

        # Check if file is already managed
        result_panel = self.query_one(ResultPanel)
        result_panel.update_working("Checking if file is already managed...")

        try:
            managed_files = ChezmoiWrapper.get_managed_files()
            if file_path in managed_files:
                result_panel.update_result(
                    f"⚠ File is already managed by chezmoi!\n"
                    f"Use 'chezmoi edit {file_path}' to modify it.",
                    success=False,
                )
                self.app.notify(
                    "File is already managed",
                    title="Already Managed",
                    severity="warning",
                )
                return
        except Exception as e:
            # If we can't check, continue anyway but log
            self.log.warning(f"Could not check managed files: {e}")

        # Get options
        options = {
            "template": self.query_one("#opt-template", Checkbox).value,
            "encrypt": self.query_one("#opt-encrypt", Checkbox).value,
            "recursive": self.query_one("#opt-recursive", Checkbox).value,
            "exact": self.query_one("#opt-exact", Checkbox).value,
            "autotemplate": self.query_one("#opt-autotemplate", Checkbox).value,
            "follow": self.query_one("#opt-follow", Checkbox).value,
            "create": self.query_one("#opt-create", Checkbox).value,
        }

        # Show working status
        result_panel.update_working(f"Adding {file_path}...")

        # Run add in background
        self.run_worker(self._add_file(file_path, options), exclusive=True, thread=True)

    async def _add_file(self, file_path: str, options: dict) -> tuple[bool, str]:
        """Add file in background worker.

        Args:
            file_path: Path to file to add.
            options: Dictionary of options.

        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            output = ChezmoiWrapper.add(targets=file_path, **options)

            # Get the source path to show user
            source_path = ChezmoiWrapper.get_source_path(file_path)

            # Build detailed success message
            message_parts = [
                "✓ [green]File added successfully![/green]",
                "",
                f"[cyan]Target:[/cyan] {file_path}",
                f"[cyan]Source:[/cyan] {source_path}",
            ]

            # Show which options were applied
            enabled_opts = [opt for opt, enabled in options.items() if enabled]
            if enabled_opts:
                message_parts.append(
                    f"[cyan]Options applied:[/cyan] {', '.join(enabled_opts)}"
                )

            # Add helpful next steps
            message_parts.append("")
            message_parts.append("[bold]Next steps:[/bold]")
            message_parts.append(f"• Edit: [dim]chezmoi edit {file_path}[/dim]")
            message_parts.append(f"• View diff: [dim]chezmoi diff {file_path}[/dim]")
            message_parts.append("• Apply changes: [dim]chezmoi apply[/dim]")

            if options.get("template"):
                message_parts.append(
                    "• [yellow]Remember to add template variables like {{ .email }}[/yellow]"
                )

            if output.strip():
                message_parts.append("")
                message_parts.append("[dim]Command output:[/dim]")
                message_parts.append(output.strip())

            return (True, "\n".join(message_parts))
        except ChezmoiCommandError as e:
            error_msg = f"✗ [red]Failed to add file[/red]\n\n{str(e)}"
            if e.stderr:
                error_msg += f"\n\n[dim]Error details:[/dim]\n{e.stderr}"

            # Add helpful suggestions based on error
            if (
                "already in source state" in str(e).lower()
                or "already in source state" in e.stderr.lower()
            ):
                error_msg += "\n\n[yellow]💡 This file is already managed. Use 'chezmoi edit' instead.[/yellow]"
            elif (
                "permission denied" in str(e).lower()
                or "permission denied" in e.stderr.lower()
            ):
                error_msg += "\n\n[yellow]💡 Check file permissions or try with sudo/elevated privileges.[/yellow]"

            return (False, error_msg)
        except Exception as e:
            return (False, f"✗ [red]Unexpected error:[/red]\n{str(e)}")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            if hasattr(event.worker, "result") and event.worker.result is not None:
                success, message = event.worker.result
                result_panel = self.query_one(ResultPanel)
                result_panel.update_result(message, success=success)

                # Notify user
                if success:
                    self.app.notify(
                        "File added successfully!",
                        title="Success",
                        severity="information",
                    )
                else:
                    self.app.notify(
                        "Failed to add file", title="Error", severity="error"
                    )

    def action_pop_screen(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
