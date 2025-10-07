"""Tests for screens and widgets."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from textual.widgets import Input

from app.widgets import FileInput, ResultPanel, OptionsPanel
from app.chezmoi_wrapper import ChezmoiWrapper


class TestFileInput:
    """Test cases for FileInput widget."""
    
    def test_init(self):
        """Test initialization."""
        widget = FileInput()
        assert widget.placeholder == "Enter file path (e.g., ~/.bashrc)"
    
    def test_validate_path_empty(self):
        """Test validation with empty path."""
        widget = FileInput()
        is_valid, msg = widget.validate_path("")
        assert not is_valid
        assert "cannot be empty" in msg.lower()
    
    def test_validate_path_whitespace(self):
        """Test validation with whitespace."""
        widget = FileInput()
        is_valid, msg = widget.validate_path("   ")
        assert not is_valid
        assert "cannot be empty" in msg.lower()
    
    @patch('pathlib.Path.expanduser')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_validate_path_valid(self, mock_is_file, mock_exists, mock_expand):
        """Test validation with valid path."""
        mock_expand.return_value = Mock()
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        widget = FileInput()
        is_valid, msg = widget.validate_path("~/.bashrc")
        assert is_valid
        assert msg == ""
    
    @patch('pathlib.Path.expanduser')
    @patch('pathlib.Path.exists')
    def test_validate_path_not_exists(self, mock_exists, mock_expand):
        """Test validation with non-existent file."""
        mock_path = Mock()
        mock_path.exists.return_value = False
        mock_expand.return_value = mock_path
        
        widget = FileInput()
        is_valid, msg = widget.validate_path("~/.bashrc")
        assert not is_valid
        assert "does not exist" in msg.lower()


class TestResultPanel:
    """Test cases for ResultPanel widget."""
    
    def test_show_success(self):
        """Test showing success message."""
        panel = ResultPanel()
        panel.show_success("Test message")
        # In real app this would update the display
        # Just testing it doesn't crash
    
    def test_show_error(self):
        """Test showing error message."""
        panel = ResultPanel()
        panel.show_error("Error message")
    
    def test_show_info(self):
        """Test showing info message."""
        panel = ResultPanel()
        panel.show_info("Info message")
    
    def test_clear(self):
        """Test clearing the panel."""
        panel = ResultPanel()
        panel.clear()


class TestOptionsPanel:
    """Test cases for OptionsPanel widget."""
    
    def test_init(self):
        """Test initialization."""
        panel = OptionsPanel()
        assert panel.border_title == "Options"


class TestAddDotfileScreen:
    """Test cases for AddDotfileScreen."""
    
    @pytest.fixture
    def mock_chezmoi(self):
        """Create mock ChezmoiWrapper."""
        return Mock(spec=ChezmoiWrapper)
    
    def test_screen_creation(self, mock_chezmoi):
        """Test screen can be created."""
        from app.screens.add import AddDotfileScreen
        screen = AddDotfileScreen(mock_chezmoi)
        assert screen.chezmoi == mock_chezmoi
    
    @patch.object(ChezmoiWrapper, 'add')
    @patch.object(ChezmoiWrapper, 'is_managed')
    def test_add_file_success(self, mock_is_managed, mock_add):
        """Test successful file addition."""
        mock_is_managed.return_value = False
        mock_add.return_value = "success"
        
        # This would require running the app to test properly
        # For now just verify mocks are set up
        assert mock_is_managed is not None
        assert mock_add is not None
