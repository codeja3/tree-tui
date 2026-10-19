import subprocess
from unittest.mock import patch

import pytest

from tree_tui.platform.clipboard import ClipboardError, copy_to_clipboard


class TestClipboard:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Clear environment variables for each test
        if "WAYLAND_DISPLAY" in globals():
            del globals()["WAYLAND_DISPLAY"]
        if "WAYLAND_DISPLAY" in globals():
            del globals()["WAYLAND_DISPLAY"]

    @patch("sys.platform", "darwin")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_macos_dispatch(self, mock_run, mock_which):
        """Test macOS clipboard dispatch with pbcopy"""
        mock_which.return_value = "/usr/bin/pbcopy"
        text = "test content"

        copy_to_clipboard(text)

        mock_which.assert_called_once_with("pbcopy")
        mock_run.assert_called_once_with(
            ["pbcopy"], input=text.encode("utf-8"), check=True
        )

    @patch("sys.platform", "linux")
    @patch("os.environ.get")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_wayland_dispatch(self, mock_run, mock_which, mock_env_get):
        """Test Wayland clipboard dispatch with wl-copy"""
        mock_env_get.return_value = "wayland"
        mock_which.side_effect = [None, "/usr/bin/wl-copy"]  # pbcopy not found, wl-copy found
        text = "test content"

        copy_to_clipboard(text)

        mock_which.assert_any_call("pbcopy")
        mock_which.assert_any_call("wl-copy")
        mock_run.assert_called_once_with(
            ["wl-copy"], input=text.encode("utf-8"), check=True
        )

    @patch("sys.platform", "linux")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_xclip_dispatch(self, mock_run, mock_which):
        """Test X11 clipboard dispatch with xclip"""
        mock_which.side_effect = [None, None, "/usr/bin/xclip"]  # pbcopy, wl-copy not found, xclip found
        text = "test content"

        copy_to_clipboard(text)

        mock_which.assert_any_call("pbcopy")
        mock_which.assert_any_call("wl-copy")
        mock_which.assert_any_call("xclip")
        mock_run.assert_called_once_with(
            ["xclip", "-selection", "clipboard"],
            input=text.encode("utf-8"),
            check=True,
        )

    @patch("sys.platform", "linux")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_xsel_fallback_dispatch(self, mock_run, mock_which):
        """Test X11 clipboard dispatch with xsel fallback"""
        mock_which.side_effect = [None, None, None, "/usr/bin/xsel"]  # pbcopy, wl-copy, xclip not found, xsel found
        text = "test content"

        copy_to_clipboard(text)

        mock_which.assert_any_call("pbcopy")
        mock_which.assert_any_call("wl-copy")
        mock_which.assert_any_call("xclip")
        mock_which.assert_any_call("xsel")
        mock_run.assert_called_once_with(
            ["xsel", "--clipboard", "--input"],
            input=text.encode("utf-8"),
            check=True,
        )

    @patch("sys.platform", "linux")
    @patch("shutil.which")
    def test_no_clipboard_tool_raises_error(self, mock_which):
        """Test that ClipboardError is raised when no clipboard tool is found"""
        mock_which.return_value = None  # All tools return None
        text = "test content"

        with pytest.raises(ClipboardError):
            copy_to_clipboard(text)

    @patch("sys.platform", "darwin")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_subprocess_called_process_error_raises_clipboard_error(
        self, mock_run, mock_which
    ):
        """Test that ClipboardError is raised when subprocess.run raises CalledProcessError"""
        mock_which.return_value = "/usr/bin/pbcopy"
        mock_run.side_effect = subprocess.CalledProcessError(1, "pbcopy")

        with pytest.raises(ClipboardError):
            copy_to_clipboard("test content")

    @patch("sys.platform", "darwin")
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_subprocess_os_error_raises_clipboard_error(
        self, mock_run, mock_which
    ):
        """Test that ClipboardError is raised when subprocess.run raises OSError"""
        mock_which.return_value = "/usr/bin/pbcopy"
        mock_run.side_effect = OSError("Permission denied")

        with pytest.raises(ClipboardError):
            copy_to_clipboard("test content")
