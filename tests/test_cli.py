from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tree_tui.cli import main


def test_read_outline_from_stdin(capsys: pytest.CaptureFixture[str]) -> None:
    """Test reading outline from STDIN when piped, printing rendered tree."""
    mock_stdin = StringIO("root\n  child1\n  child2\n")

    with patch("sys.stdin", mock_stdin), patch("sys.stdin.isatty", return_value=False):
        exit_code = main([])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "root" in captured.out
        assert "child1" in captured.out
        assert "child2" in captured.out


def test_read_outline_from_file_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test reading outline from file path argument."""
    file_path = tmp_path / "outline.txt"
    file_path.write_text("my_dir/\n  file.txt\n")

    exit_code = main([str(file_path)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "my_dir/" in captured.out
    assert "file.txt" in captured.out


def test_ascii_mode_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test ASCII mode flag (--ascii or -a)."""
    file_path = tmp_path / "outline.txt"
    file_path.write_text("root\n  child1\n  child2\n")

    exit_code = main(["--ascii", str(file_path)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "|-- child1" in captured.out
    assert "`-- child2" in captured.out


def test_shell_command_generator_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test shell command generator flag (-c or --generate-command)."""
    file_path = tmp_path / "outline.txt"
    file_path.write_text("root/\n  src/\n    main.py\n")

    exit_code = main(["-c", str(file_path)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "mkdir -p src" in captured.out
    assert "touch src/main.py" in captured.out


def test_one_liner_with_command_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test --one-liner combined with -c."""
    file_path = tmp_path / "outline.txt"
    file_path.write_text("root/\n  src/\n    main.py\n")

    exit_code = main(["-c", "--one-liner", str(file_path)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "mkdir -p src && touch src/main.py" in captured.out.strip()


def test_tui_mode_when_stdin_is_tty() -> None:
    """Test opening TUI mode when STDIN is a TTY and no file argument is given."""
    mock_app = MagicMock()
    with patch("sys.stdin.isatty", return_value=True), patch("tree_tui.cli._launch_tui", mock_app):
        exit_code = main([])
        assert exit_code == 0
        mock_app.assert_called_once()


def test_exit_code_on_file_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    """Test exit code 1 on file not found."""
    exit_code = main(["nonexistent_outline_file.txt"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_exit_code_on_invalid_outline(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test exit code 2 on invalid indentation jump."""
    file_path = tmp_path / "bad.txt"
    file_path.write_text("root\n    child\n          jump\n")

    exit_code = main([str(file_path)])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Error" in captured.err
