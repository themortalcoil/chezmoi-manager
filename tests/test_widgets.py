"""Unit tests for custom widgets."""

from pathlib import Path

import pytest

from app.widgets.file_input import FileInput


class TestFileInput:
    """Test cases for FileInput widget."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_file_input_initialization(self):
        """Test FileInput initializes with placeholder."""
        widget = FileInput(placeholder="Test placeholder")
        assert widget.placeholder == "Test placeholder"
        assert widget.file_path == ""
        assert widget.is_valid is False

    @pytest.mark.unit
    def test_get_path_basic(self):
        """Test get_path returns the file path."""
        widget = FileInput()
        widget.file_path = "/tmp/test.txt"
        assert widget.get_path() == "/tmp/test.txt"

    @pytest.mark.unit
    def test_get_path_with_tilde(self):
        """Test get_path expands tilde."""
        widget = FileInput()
        widget.file_path = "~/test.txt"
        result = widget.get_path()
        assert result.startswith("/")
        assert not result.startswith("~")

    @pytest.mark.unit
    def test_get_path_obj_returns_path(self):
        """Test get_path_obj returns Path object."""
        widget = FileInput()
        widget.file_path = "/tmp/test.txt"
        result = widget.get_path_obj()
        assert isinstance(result, Path)
        assert str(result) == "/tmp/test.txt"

    @pytest.mark.unit
    def test_get_path_strips_whitespace(self):
        """Test get_path strips whitespace."""
        widget = FileInput()
        widget.file_path = "  /tmp/test.txt  "
        assert widget.get_path() == "/tmp/test.txt"

    @pytest.mark.unit
    def test_file_path_reactive_default(self):
        """Test file_path reactive property defaults to empty."""
        widget = FileInput()
        assert widget.file_path == ""

    @pytest.mark.unit
    def test_is_valid_reactive_default(self):
        """Test is_valid reactive property defaults to False."""
        widget = FileInput()
        assert widget.is_valid is False
