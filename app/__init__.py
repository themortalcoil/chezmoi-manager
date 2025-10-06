"""Chezmoi Manager application package."""

__version__ = "0.1.0"

__all__ = [
    "ChezmoiWrapper",
    "ChezmoiCommandError",
]

from .chezmoi_wrapper import ChezmoiWrapper, ChezmoiCommandError
