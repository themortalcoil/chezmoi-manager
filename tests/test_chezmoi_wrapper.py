"""Tests for ChezmoiWrapper."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.chezmoi_wrapper import ChezmoiWrapper, ChezmoiCommandError


class TestChezmoiWrapper:
    """Test cases for ChezmoiWrapper."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.wrapper = ChezmoiWrapper()
    
    def test_init(self):
        """Test initialization."""
        wrapper = ChezmoiWrapper("custom_path")
        assert wrapper.chezmoi_path == "custom_path"
    
    def test_init_default(self):
        """Test default initialization."""
        assert self.wrapper.chezmoi_path == "chezmoi"
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = Mock(
            stdout="success",
            stderr="",
            returncode=0
        )
        
        stdout, stderr, code = self.wrapper._run_command("status")
        
        assert stdout == "success"
        assert stderr == ""
        assert code == 0
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test command failure."""
        mock_run.return_value = Mock(
            stdout="",
            stderr="error",
            returncode=1
        )
        
        with pytest.raises(ChezmoiCommandError):
            self.wrapper._run_command("bad_command")
    
    @patch('subprocess.run')
    def test_run_command_no_check(self, mock_run):
        """Test command with check=False."""
        mock_run.return_value = Mock(
            stdout="",
            stderr="error",
            returncode=1
        )
        
        stdout, stderr, code = self.wrapper._run_command("cmd", check=False)
        assert code == 1
    
    @patch('subprocess.run')
    def test_add_basic(self, mock_run):
        """Test basic file addition."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.add("~/.bashrc")
        
        assert result == "added"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "add" in args
        assert "~/.bashrc" in args
    
    @patch('subprocess.run')
    def test_add_with_template(self, mock_run):
        """Test adding file with template option."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", template=True)
        
        args = mock_run.call_args[0][0]
        assert "--template" in args
    
    @patch('subprocess.run')
    def test_add_with_encrypt(self, mock_run):
        """Test adding file with encrypt option."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", encrypt=True)
        
        args = mock_run.call_args[0][0]
        assert "--encrypt" in args
    
    @patch('subprocess.run')
    def test_add_with_private(self, mock_run):
        """Test adding file with private option."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", private=True)
        
        args = mock_run.call_args[0][0]
        assert "--private" in args
    
    @patch('subprocess.run')
    def test_add_with_executable(self, mock_run):
        """Test adding file with executable option."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", executable=True)
        
        args = mock_run.call_args[0][0]
        assert "--executable" in args
    
    @patch('subprocess.run')
    def test_add_with_readonly(self, mock_run):
        """Test adding file with readonly option."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", readonly=True)
        
        args = mock_run.call_args[0][0]
        assert "--readonly" in args
    
    @patch('subprocess.run')
    def test_add_with_exact(self, mock_run):
        """Test adding file with exact option."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", exact=True)
        
        args = mock_run.call_args[0][0]
        assert "--exact" in args
    
    @patch('subprocess.run')
    def test_add_with_multiple_options(self, mock_run):
        """Test adding file with multiple options."""
        mock_run.return_value = Mock(
            stdout="added",
            stderr="",
            returncode=0
        )
        
        self.wrapper.add("~/.bashrc", template=True, private=True, executable=True)
        
        args = mock_run.call_args[0][0]
        assert "--template" in args
        assert "--private" in args
        assert "--executable" in args
    
    @patch('subprocess.run')
    def test_remove(self, mock_run):
        """Test file removal."""
        mock_run.return_value = Mock(
            stdout="removed",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.remove("~/.bashrc")
        
        assert result == "removed"
        args = mock_run.call_args[0][0]
        assert "remove" in args
        assert "~/.bashrc" in args
    
    @patch('subprocess.run')
    def test_diff_all(self, mock_run):
        """Test diff for all files."""
        mock_run.return_value = Mock(
            stdout="diff output",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.diff()
        
        assert result == "diff output"
        args = mock_run.call_args[0][0]
        assert "diff" in args
    
    @patch('subprocess.run')
    def test_diff_specific_file(self, mock_run):
        """Test diff for specific file."""
        mock_run.return_value = Mock(
            stdout="diff output",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.diff("~/.bashrc")
        
        assert result == "diff output"
        args = mock_run.call_args[0][0]
        assert "diff" in args
        assert "~/.bashrc" in args
    
    @patch('subprocess.run')
    def test_apply_all(self, mock_run):
        """Test apply for all files."""
        mock_run.return_value = Mock(
            stdout="applied",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.apply()
        
        assert result == "applied"
        args = mock_run.call_args[0][0]
        assert "apply" in args
    
    @patch('subprocess.run')
    def test_apply_specific_file(self, mock_run):
        """Test apply for specific file."""
        mock_run.return_value = Mock(
            stdout="applied",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.apply("~/.bashrc")
        
        assert result == "applied"
        args = mock_run.call_args[0][0]
        assert "apply" in args
        assert "~/.bashrc" in args
    
    @patch('subprocess.run')
    def test_managed(self, mock_run):
        """Test getting managed files."""
        mock_run.return_value = Mock(
            stdout="~/.bashrc\n~/.vimrc\n~/.gitconfig\n",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.managed()
        
        assert len(result) == 3
        assert "~/.bashrc" in result
        assert "~/.vimrc" in result
        assert "~/.gitconfig" in result
    
    @patch('subprocess.run')
    def test_status(self, mock_run):
        """Test getting status."""
        mock_run.return_value = Mock(
            stdout="status output",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.status()
        
        assert result == "status output"
        args = mock_run.call_args[0][0]
        assert "status" in args
    
    @patch('pathlib.Path.expanduser')
    @patch('pathlib.Path.resolve')
    @patch('subprocess.run')
    def test_is_managed_true(self, mock_run, mock_resolve, mock_expand):
        """Test is_managed returns True for managed file."""
        # Mock Path operations to return consistent paths
        mock_path = Mock()
        mock_path.resolve.return_value = mock_path
        mock_path.__str__ = Mock(return_value="/home/user/.bashrc")
        mock_expand.return_value = mock_path
        mock_resolve.return_value = mock_path
        
        mock_run.return_value = Mock(
            stdout="/home/user/.bashrc\n",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.is_managed("~/.bashrc")
        
        assert result is True
    
    @patch('subprocess.run')
    def test_is_managed_false(self, mock_run):
        """Test is_managed returns False for unmanaged file."""
        mock_run.return_value = Mock(
            stdout="~/.vimrc\n",
            stderr="",
            returncode=0
        )
        
        result = self.wrapper.is_managed("~/.bashrc")
        
        assert result is False
    
    @patch('subprocess.run')
    def test_is_managed_error(self, mock_run):
        """Test is_managed handles errors gracefully."""
        mock_run.return_value = Mock(
            stdout="",
            stderr="error",
            returncode=1
        )
        
        result = self.wrapper.is_managed("~/.bashrc")
        
        assert result is False
