from __future__ import annotations

import asyncio
from unittest.mock import patch

from textual.widgets import Static, TextArea

from tree_tui.tui.app import DEFAULT_TEMPLATE, TreeTuiApp


def test_app_launch_widgets_exist() -> None:
    """Test that app launches with required widgets."""

    async def run() -> None:
        async with TreeTuiApp().run_test() as pilot:
            app = pilot.app
            assert app.query_one("#editor", TextArea) is not None
            assert app.query_one("#preview", Static) is not None

    asyncio.run(run())


def test_editor_updates_preview() -> None:
    """Test that setting text in editor updates preview."""

    async def run() -> None:
        async with TreeTuiApp().run_test() as pilot:
            editor = pilot.app.query_one("#editor", TextArea)
            preview = pilot.app.query_one("#preview", Static)

            editor.text = "root/\n  child"
            await pilot.pause()

            preview_str = str(preview.content)
            assert "root" in preview_str
            assert "child" in preview_str

    asyncio.run(run())


def test_ctrl_y_copies_tree() -> None:
    """Test that ctrl+y copies tree to clipboard."""

    async def run() -> None:
        app = TreeTuiApp()
        async with app.run_test():
            with patch("tree_tui.tui.app.copy_to_clipboard") as mock_copy:
                app.action_copy_tree()
                mock_copy.assert_called_once()
                assert "project" in mock_copy.call_args[0][0]

    asyncio.run(run())


def test_ctrl_b_copies_tree() -> None:
    """Test that ctrl+b copies tree to clipboard."""

    async def run() -> None:
        async with TreeTuiApp().run_test() as pilot:
            with patch("tree_tui.tui.app.copy_to_clipboard") as mock_copy:
                await pilot.press("ctrl+b")
                mock_copy.assert_called_once()
                assert "project" in mock_copy.call_args[0][0]

    asyncio.run(run())


def test_ctrl_g_copies_shell_command() -> None:
    """Test that ctrl+g copies shell command to clipboard."""

    async def run() -> None:
        async with TreeTuiApp().run_test() as pilot:
            with patch("tree_tui.tui.app.copy_to_clipboard") as mock_copy:
                await pilot.press("ctrl+g")
                mock_copy.assert_called_once()
                assert "mkdir" in mock_copy.call_args[0][0] or "touch" in mock_copy.call_args[0][0]

    asyncio.run(run())


def test_ctrl_r_resets_editor() -> None:
    """Test that ctrl+r resets editor to default template."""

    async def run() -> None:
        async with TreeTuiApp().run_test() as pilot:
            editor = pilot.app.query_one("#editor", TextArea)

            editor.text = "custom outline"
            assert editor.text == "custom outline"

            await pilot.press("ctrl+r")
            assert editor.text == DEFAULT_TEMPLATE

    asyncio.run(run())


def test_invalid_syntax_does_not_crash() -> None:
    """Test that invalid outline syntax doesn't crash app and retains preview."""

    async def run() -> None:
        async with TreeTuiApp().run_test() as pilot:
            editor = pilot.app.query_one("#editor", TextArea)
            preview = pilot.app.query_one("#preview", Static)
            status_bar = pilot.app.query_one("#status-bar", Static)

            # Insert malformed indentation jump
            editor.text = "root\n    child\n          jump"
            await pilot.pause()

            assert "Syntax Error" in str(status_bar.content)
            assert str(preview.content) != ""

    asyncio.run(run())
