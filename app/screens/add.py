"""Screen for adding dotfiles to chezmoi."""

from textual import on
from textual.widgets import Button, Label, ListView, ListItem, Static
from textual.containers import Container, Vertical, Horizontal

from ..base_screen import BaseScreen
from ..chezmoi_wrapper import ChezmoiWrapper, ChezmoiCommandError
from ..widgets import FileInput, OptionsPanel, ResultPanel, PreviewPanel
from ..constants import (
    COMMON_DOTFILES,
    BUTTON_BROWSE,
    BUTTON_SUBMIT,
    BUTTON_CANCEL,
    MSG_SUCCESS_ADDED,
    MSG_ERROR_ALREADY_MANAGED,
)


class CommonFilesPanel(ListView):
    """Panel showing common dotfiles for quick selection."""
    
    def compose(self):
        """Compose the common files list."""
        for file_path in COMMON_DOTFILES:
            item = ListItem(Label(file_path), classes="common-file-item")
            item.file_path = file_path  # Store as custom attribute
            yield item


class AddDotfileScreen(BaseScreen):
    """Screen for adding files to chezmoi with enhanced UI."""
    
    CSS = """
    AddDotfileScreen {
        align: center middle;
        layout: vertical;
    }
    
    #add_container {
        width: 80;
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    
    .section {
        margin: 1 0;
        height: auto;
    }
    
    .common-file-item {
        padding: 0 1;
    }
    
    .common-file-item:hover {
        background: $boost;
    }
    
    CommonFilesPanel {
        height: 10;
        border: solid $accent;
        margin: 1 0;
    }
    
    FileInput {
        margin: 1 0;
    }
    
    OptionsPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
    }
    
    PreviewPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
        margin: 1 0;
    }
    
    ResultPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
        margin: 1 0;
        min-height: 3;
    }
    
    .button-row {
        layout: horizontal;
        height: auto;
        align: center middle;
    }
    
    .button-row Button {
        margin: 0 1;
    }
    
    .preset-row {
        layout: horizontal;
        height: auto;
        margin: 1 0;
    }
    
    .preset-row Button {
        margin: 0 1;
        min-width: 15;
    }
    """
    
    def __init__(self, chezmoi: ChezmoiWrapper, *args, **kwargs):
        """Initialize the screen.
        
        Args:
            chezmoi: ChezmoiWrapper instance
        """
        super().__init__(*args, **kwargs)
        self.chezmoi = chezmoi
    
    def compose(self):
        """Compose the screen layout."""
        with Container(id="add_container"):
            yield Label("Add File to Chezmoi", classes="section")
            yield FileInput(id="file_input", classes="section")
            
            with Horizontal(classes="button-row section"):
                yield Button(f"📁 Browse Files", id=BUTTON_BROWSE)
            
            yield Label("Common Files", classes="section")
            yield CommonFilesPanel(id="common_files")
            
            yield Label("Quick Presets", classes="section")
            with Horizontal(classes="preset-row"):
                yield Button("Private Config", id="preset_private")
                yield Button("Template", id="preset_template")
                yield Button("Executable", id="preset_executable")
                yield Button("Readonly", id="preset_readonly")
            
            yield Label("Advanced Options", classes="section")
            yield OptionsPanel(id="options_panel")
            
            yield PreviewPanel(id="preview_panel", classes="section")
            yield ResultPanel(id="result_panel", classes="section")
            
            with Horizontal(classes="button-row section"):
                yield Button("Add File", variant="primary", id=BUTTON_SUBMIT)
                yield Button("Cancel", id=BUTTON_CANCEL)
    
    def on_mount(self) -> None:
        """Handle mount event."""
        self.query_one("#file_input").focus()
        self._update_preview()
    
    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection from common files list."""
        if event.item and hasattr(event.item, 'file_path'):
            file_path = event.item.file_path
            file_input = self.query_one("#file_input", FileInput)
            file_input.value = file_path
            self._update_preview()
            file_input.focus()
    
    @on(FileInput.Changed)
    def on_file_input_changed(self, event: FileInput.Changed) -> None:
        """Handle file input changes."""
        self._update_preview()
    
    @on(Button.Pressed, "#preset_private")
    def on_preset_private(self) -> None:
        """Apply private preset."""
        options = self.query_one("#options_panel", OptionsPanel)
        options.reset()
        self.query_one("#private_check").value = True
        self._update_preview()
    
    @on(Button.Pressed, "#preset_template")
    def on_preset_template(self) -> None:
        """Apply template preset."""
        options = self.query_one("#options_panel", OptionsPanel)
        options.reset()
        options.query_one("#template_check").value = True
        self._update_preview()
    
    @on(Button.Pressed, "#preset_executable")
    def on_preset_executable(self) -> None:
        """Apply executable preset."""
        options = self.query_one("#options_panel", OptionsPanel)
        options.reset()
        self.query_one("#executable_check").value = True
        self._update_preview()
    
    @on(Button.Pressed, "#preset_readonly")
    def on_preset_readonly(self) -> None:
        """Apply readonly preset."""
        options = self.query_one("#options_panel", OptionsPanel)
        options.reset()
        self.query_one("#readonly_check").value = True
        self._update_preview()
    
    def _update_preview(self) -> None:
        """Update the preview panel."""
        file_input = self.query_one("#file_input", FileInput)
        options = self.query_one("#options_panel", OptionsPanel)
        preview = self.query_one("#preview_panel", PreviewPanel)
        
        preview.update_preview(file_input.value, options.get_options())
    
    @on(Button.Pressed, f"#{BUTTON_BROWSE}")
    def on_browse_pressed(self) -> None:
        """Handle browse button press."""
        from .browse import FileBrowserScreen
        self.app.push_screen(FileBrowserScreen(self.chezmoi), self._handle_browse_result)
    
    def _handle_browse_result(self, result: str | None) -> None:
        """Handle result from file browser.
        
        Args:
            result: Selected file path or None
        """
        if result:
            file_input = self.query_one("#file_input", FileInput)
            file_input.value = result
            self._update_preview()
    
    @on(Button.Pressed, f"#{BUTTON_SUBMIT}")
    def on_submit_pressed(self) -> None:
        """Handle submit button press."""
        file_input = self.query_one("#file_input", FileInput)
        result_panel = self.query_one("#result_panel", ResultPanel)
        
        # Validate input
        is_valid, error_msg = file_input.validate_path(file_input.value)
        if not is_valid:
            result_panel.show_error(error_msg)
            return
        
        # Check if already managed
        if self.chezmoi.is_managed(file_input.value):
            result_panel.show_error(
                f"{MSG_ERROR_ALREADY_MANAGED}. Use 'Edit' to modify it instead."
            )
            return
        
        # Get options and add file
        options = self.query_one("#options_panel", OptionsPanel)
        self._add_file(file_input.value, options.get_options())
    
    def _add_file(self, path: str, options: dict[str, bool]) -> None:
        """Add file to chezmoi.
        
        Args:
            path: File path to add
            options: Dictionary of options
        """
        try:
            self.chezmoi.add(path, **options)
            self._handle_add_complete(True, path, options)
        except ChezmoiCommandError as e:
            self._handle_add_complete(False, path, options, str(e))
    
    def _handle_add_complete(self, success: bool, path: str, options: dict, error: str = "") -> None:
        """Handle file addition completion.
        
        Args:
            success: Whether the operation succeeded
            path: File path
            options: Options used
            error: Error message if failed
        """
        result_panel = self.query_one("#result_panel", ResultPanel)
        
        if success:
            enabled_opts = [k for k, v in options.items() if v]
            opts_str = f" ({', '.join(enabled_opts)})" if enabled_opts else ""
            
            message = (
                f"[green]{MSG_SUCCESS_ADDED}[/green]\n"
                f"[bold]File:[/bold] {path}{opts_str}\n"
                f"[dim]Next: Run 'chezmoi diff' to review changes[/dim]"
            )
            
            if options.get("template"):
                message += "\n[yellow]💡 Don't forget to use template variables![/yellow]"
            
            result_panel.update(message)
            
            # Clear form
            self.query_one("#file_input").value = ""
            self.query_one("#options_panel", OptionsPanel).reset()
            self._update_preview()
        else:
            result_panel.show_error(f"Failed to add file: {error}")
    
    @on(Button.Pressed, f"#{BUTTON_CANCEL}")
    def on_cancel_pressed(self) -> None:
        """Handle cancel button press."""
        self.app.pop_screen()

