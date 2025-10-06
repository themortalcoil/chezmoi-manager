"""Constants for the chezmoi-manager application."""

# Application metadata
VERSION = "v0.1.0"
APP_NAME = "Chezmoi Manager"

# Button IDs
BUTTON_ADD = "add_button"
BUTTON_DIFF = "diff_button"
BUTTON_EDIT = "edit_button"
BUTTON_REMOVE = "remove_button"
BUTTON_LIST = "list_button"
BUTTON_APPLY = "apply_button"
BUTTON_BROWSE = "browse_button"
BUTTON_REFRESH = "refresh_button"
BUTTON_EXPORT = "export_button"
BUTTON_BACK = "back_button"
BUTTON_SUBMIT = "submit_button"
BUTTON_CANCEL = "cancel_button"

# Common dotfiles
COMMON_DOTFILES = [
    "~/.bashrc",
    "~/.zshrc",
    "~/.vimrc",
    "~/.gitconfig",
    "~/.ssh/config",
    "~/.tmux.conf",
    "~/.config/nvim/init.vim",
    "~/.config/fish/config.fish",
]

# Preset configurations
PRESET_PRIVATE = "private"
PRESET_TEMPLATE = "template"
PRESET_EXECUTABLE = "executable"
PRESET_READONLY = "readonly"

# Messages
MSG_SUCCESS_ADDED = "File added successfully!"
MSG_SUCCESS_REMOVED = "File removed successfully!"
MSG_SUCCESS_APPLIED = "Changes applied successfully!"
MSG_ERROR_ALREADY_MANAGED = "This file is already managed by chezmoi"
MSG_ERROR_FILE_NOT_FOUND = "File not found"
MSG_ERROR_PERMISSION_DENIED = "Permission denied"
