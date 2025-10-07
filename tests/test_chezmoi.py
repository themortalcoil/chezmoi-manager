"""Unit tests for ChezmoiWrapper class."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from chezmoi import ChezmoiCommandError, ChezmoiNotFoundError, ChezmoiWrapper


class TestChezmoiWrapper:
    """Test cases for ChezmoiWrapper class."""

    @pytest.mark.unit
    def test_check_installed_success(self):
        """Test check_installed returns True when chezmoi is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = ChezmoiWrapper.check_installed()
            assert result is True
            mock_run.assert_called_once()

    @pytest.mark.unit
    def test_check_installed_not_found(self):
        """Test check_installed returns False when chezmoi is not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = ChezmoiWrapper.check_installed()
            assert result is False

    @pytest.mark.unit
    def test_check_installed_subprocess_error(self):
        """Test check_installed handles subprocess errors."""
        with patch("subprocess.run", side_effect=subprocess.SubprocessError):
            result = ChezmoiWrapper.check_installed()
            assert result is False

    @pytest.mark.unit
    def test_get_version_success(self):
        """Test get_version returns version string."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="chezmoi version v2.65.2\n"
            )
            version = ChezmoiWrapper.get_version()
            assert version == "chezmoi version v2.65.2"

    @pytest.mark.unit
    def test_get_version_not_found(self):
        """Test get_version raises error when chezmoi not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(ChezmoiNotFoundError):
                ChezmoiWrapper.get_version()

    @pytest.mark.unit
    def test_run_command_success(self):
        """Test run_command executes successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
            result = ChezmoiWrapper.run_command(["status"])
            assert result.returncode == 0
            assert result.stdout == "output"

    @pytest.mark.unit
    def test_run_command_with_format(self):
        """Test run_command with format flag."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="{}")
            ChezmoiWrapper.run_command(["data"], format="json")
            # Verify --format json was added to command
            call_args = mock_run.call_args[0][0]
            assert "--format" in call_args
            assert "json" in call_args

    @pytest.mark.unit
    def test_run_command_not_found(self):
        """Test run_command raises error when chezmoi not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(ChezmoiNotFoundError):
                ChezmoiWrapper.run_command(["status"])

    @pytest.mark.unit
    def test_get_status_success(self):
        """Test get_status returns status output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="M .bashrc\n")
            status = ChezmoiWrapper.get_status()
            assert status == "M .bashrc\n"

    @pytest.mark.unit
    def test_get_status_with_targets(self):
        """Test get_status with specific targets."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.get_status(targets=[".bashrc", ".vimrc"])
            call_args = mock_run.call_args[0][0]
            assert ".bashrc" in call_args
            assert ".vimrc" in call_args

    @pytest.mark.unit
    def test_get_managed_files_success(self):
        """Test get_managed_files returns list of files."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=".bashrc\n.vimrc\n.tmux.conf\n"
            )
            files = ChezmoiWrapper.get_managed_files()
            assert files == [".bashrc", ".vimrc", ".tmux.conf"]

    @pytest.mark.unit
    def test_get_managed_files_empty(self):
        """Test get_managed_files with no files."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            files = ChezmoiWrapper.get_managed_files()
            assert files == []

    @pytest.mark.unit
    def test_get_diff_success(self):
        """Test get_diff returns diff output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="diff output")
            diff = ChezmoiWrapper.get_diff()
            assert diff == "diff output"

    @pytest.mark.unit
    def test_get_diff_with_target(self):
        """Test get_diff with specific target."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.get_diff(target=".bashrc")
            call_args = mock_run.call_args[0][0]
            assert ".bashrc" in call_args

    @pytest.mark.unit
    def test_apply_success(self):
        """Test apply executes successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="applied")
            output = ChezmoiWrapper.apply()
            assert output == "applied"

    @pytest.mark.unit
    def test_apply_with_options(self):
        """Test apply with various options."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.apply(targets=[".bashrc"], dry_run=True, verbose=False)
            call_args = mock_run.call_args[0][0]
            assert ".bashrc" in call_args
            assert "--dry-run" in call_args
            assert "--verbose" not in call_args

    @pytest.mark.unit
    def test_apply_failure(self):
        """Test apply raises error on failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            with pytest.raises(ChezmoiCommandError) as exc_info:
                ChezmoiWrapper.apply()
            assert exc_info.value.returncode == 1
            assert exc_info.value.stderr == "error"

    @pytest.mark.unit
    def test_get_data_success(self):
        """Test get_data returns parsed JSON."""
        test_data = {"user": "test", "email": "test@example.com"}
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=json.dumps(test_data)
            )
            data = ChezmoiWrapper.get_data()
            assert data == test_data

    @pytest.mark.unit
    def test_get_data_invalid_json(self):
        """Test get_data handles invalid JSON."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="invalid json")
            data = ChezmoiWrapper.get_data()
            assert data == {}

    @pytest.mark.unit
    def test_get_source_path_success(self):
        """Test get_source_path returns path."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="/home/user/.local/share/chezmoi\n"
            )
            path = ChezmoiWrapper.get_source_path()
            assert path == "/home/user/.local/share/chezmoi"

    @pytest.mark.unit
    def test_get_source_dir_success(self):
        """Test get_source_dir returns Path object."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="/home/user/.local/share/chezmoi\n"
            )
            path = ChezmoiWrapper.get_source_dir()
            assert isinstance(path, Path)
            assert str(path) == "/home/user/.local/share/chezmoi"

    @pytest.mark.unit
    def test_doctor_success(self):
        """Test doctor returns output."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok")
            output = ChezmoiWrapper.doctor()
            assert output == "ok"

    @pytest.mark.unit
    def test_verify_success(self):
        """Test verify returns success."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="verified\n", stderr=""
            )
            success, output = ChezmoiWrapper.verify()
            assert success is True
            assert output == "verified"

    @pytest.mark.unit
    def test_verify_failure(self):
        """Test verify returns failure with stderr."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="error message\n"
            )
            success, output = ChezmoiWrapper.verify()
            assert success is False
            assert output == "error message"

    @pytest.mark.unit
    def test_add_single_file(self):
        """Test add with single file."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.add(".bashrc")
            call_args = mock_run.call_args[0][0]
            assert "add" in call_args
            assert ".bashrc" in call_args

    @pytest.mark.unit
    def test_add_multiple_files(self):
        """Test add with multiple files."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.add([".bashrc", ".vimrc"])
            call_args = mock_run.call_args[0][0]
            assert ".bashrc" in call_args
            assert ".vimrc" in call_args

    @pytest.mark.unit
    def test_add_with_all_options(self):
        """Test add with all options enabled."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.add(
                ".bashrc",
                template=True,
                encrypt=True,
                recursive=False,
                exact=True,
                autotemplate=True,
                follow=True,
                create=True,
                prompt=True,
            )
            call_args = mock_run.call_args[0][0]
            assert "--template" in call_args
            assert "--encrypt" in call_args
            assert "--recursive=false" in call_args
            assert "--exact" in call_args
            assert "--autotemplate" in call_args
            assert "--follow" in call_args
            assert "--create" in call_args
            assert "--prompt" in call_args

    @pytest.mark.unit
    def test_add_failure(self):
        """Test add raises error on failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="file not found"
            )
            with pytest.raises(ChezmoiCommandError) as exc_info:
                ChezmoiWrapper.add(".nonexistent")
            assert exc_info.value.returncode == 1

    @pytest.mark.unit
    def test_remove_success(self):
        """Test remove executes successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.remove(".bashrc")
            call_args = mock_run.call_args[0][0]
            assert "remove" in call_args
            assert ".bashrc" in call_args

    @pytest.mark.unit
    def test_remove_failure(self):
        """Test remove raises error on failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            with pytest.raises(ChezmoiCommandError):
                ChezmoiWrapper.remove(".bashrc")

    @pytest.mark.unit
    def test_update_success(self):
        """Test update executes successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="updated")
            output = ChezmoiWrapper.update()
            assert output == "updated"

    @pytest.mark.unit
    def test_update_no_apply(self):
        """Test update with no apply option."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.update(apply=False)
            call_args = mock_run.call_args[0][0]
            assert "--no-apply" in call_args

    @pytest.mark.unit
    def test_init_success(self):
        """Test init executes successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.init()
            call_args = mock_run.call_args[0][0]
            assert "init" in call_args

    @pytest.mark.unit
    def test_init_with_repo(self):
        """Test init with repository URL."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            ChezmoiWrapper.init("https://github.com/user/dotfiles.git")
            call_args = mock_run.call_args[0][0]
            assert "https://github.com/user/dotfiles.git" in call_args

    @pytest.mark.unit
    def test_init_failure(self):
        """Test init raises error on failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            with pytest.raises(ChezmoiCommandError):
                ChezmoiWrapper.init()
