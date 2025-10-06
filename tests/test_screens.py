"""Unit tests for screen components."""

from unittest.mock import MagicMock, patch

import pytest

from app.screens.add import AddDotfileScreen, OptionsPanel, ResultPanel
from chezmoi import ChezmoiCommandError


class TestResultPanel:
    """Test cases for ResultPanel widget."""

    @pytest.mark.unit
    def test_result_panel_initialization(self):
        """Test ResultPanel initializes correctly."""
        panel = ResultPanel()
        assert panel is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_result_success(self, mocker):
        """Test update_result with success message."""
        panel = ResultPanel()
        # Mock the query_one method
        mock_label = MagicMock()
        mocker.patch.object(panel, "query_one", return_value=mock_label)

        panel.update_result("Test success", success=True)
        mock_label.update.assert_called_once_with("[green]Test success[/green]")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_result_failure(self, mocker):
        """Test update_result with failure message."""
        panel = ResultPanel()
        mock_label = MagicMock()
        mocker.patch.object(panel, "query_one", return_value=mock_label)

        panel.update_result("Test failure", success=False)
        mock_label.update.assert_called_once_with("[red]Test failure[/red]")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_working(self, mocker):
        """Test update_working displays working message."""
        panel = ResultPanel()
        mock_label = MagicMock()
        mocker.patch.object(panel, "query_one", return_value=mock_label)

        panel.update_working("Working...")
        mock_label.update.assert_called_once_with("[yellow]Working...[/yellow]")


class TestOptionsPanel:
    """Test cases for OptionsPanel widget."""

    @pytest.mark.unit
    def test_options_panel_initialization(self):
        """Test OptionsPanel initializes correctly."""
        panel = OptionsPanel()
        assert panel is not None


class TestAddDotfileScreen:
    """Test cases for AddDotfileScreen."""

    @pytest.mark.unit
    def test_add_dotfile_screen_initialization(self):
        """Test AddDotfileScreen initializes correctly."""
        screen = AddDotfileScreen()
        assert screen is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_file_worker_success(self):
        """Test _add_file worker with successful add."""
        screen = AddDotfileScreen()

        with patch("app.screens.add.ChezmoiWrapper.add") as mock_add:
            with patch("app.screens.add.ChezmoiWrapper.get_source_path") as mock_path:
                mock_add.return_value = ""
                mock_path.return_value = "/home/user/.local/share/chezmoi/dot_bashrc"

                success, message = await screen._add_file(
                    "/home/user/.bashrc",
                    {
                        "template": False,
                        "encrypt": False,
                        "recursive": True,
                        "exact": False,
                        "autotemplate": False,
                        "follow": False,
                        "create": False,
                    },
                )

                assert success is True
                assert "File added successfully" in message
                assert "/home/user/.local/share/chezmoi/dot_bashrc" in message

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_file_worker_failure(self):
        """Test _add_file worker with failed add."""
        screen = AddDotfileScreen()

        with patch("app.screens.add.ChezmoiWrapper.add") as mock_add:
            mock_add.side_effect = ChezmoiCommandError(
                "Failed to add", stderr="file not found", returncode=1
            )

            success, message = await screen._add_file(
                "/nonexistent/file",
                {
                    "template": False,
                    "encrypt": False,
                    "recursive": True,
                    "exact": False,
                    "autotemplate": False,
                    "follow": False,
                    "create": False,
                },
            )

            assert success is False
            assert "Failed to add file" in message
            assert "file not found" in message

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_add_file_worker_unexpected_error(self):
        """Test _add_file worker with unexpected error."""
        screen = AddDotfileScreen()

        with patch("app.screens.add.ChezmoiWrapper.add") as mock_add:
            mock_add.side_effect = Exception("Unexpected error")

            success, message = await screen._add_file(
                "/home/user/.bashrc",
                {
                    "template": False,
                    "encrypt": False,
                    "recursive": True,
                    "exact": False,
                    "autotemplate": False,
                    "follow": False,
                    "create": False,
                },
            )

            assert success is False
            assert "Unexpected error" in message
