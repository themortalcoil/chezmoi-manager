"""Screen modules for the application."""

__all__ = [
    "AddDotfileScreen",
    "DiffScreen",
    "EditScreen",
    "RemoveScreen",
    "ListScreen",
    "FileBrowserScreen",
]

from .add import AddDotfileScreen
from .diff import DiffScreen
from .edit import EditScreen
from .remove import RemoveScreen
from .list import ListScreen
from .browse import FileBrowserScreen
