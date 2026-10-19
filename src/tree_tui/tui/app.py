from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Static, TextArea

from tree_tui.core.generator import generate_shell_command
from tree_tui.core.parser import parse_outline
from tree_tui.core.renderer import GLYPHS_UNICODE, render_tree
from tree_tui.platform.clipboard import ClipboardError, copy_to_clipboard

DEFAULT_TEMPLATE = """project/
  src/
    main.py
    utils.py
  tests/
    test_main.py
  README.md
"""


class HelpScreen(ModalScreen[None]):
    """Modal help screen displaying keyboard shortcuts."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "dismiss", "Close"),
        Binding("f1", "dismiss", "Close"),
        Binding("?", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        help_text = (
            "[bold]tree-tui Keyboard Shortcuts[/bold]\n\n"
            "  [bold cyan]Ctrl+Y[/bold cyan] / [bold cyan]Ctrl+B[/bold cyan] : Copy rendered tree to clipboard\n"
            "  [bold cyan]Ctrl+G[/bold cyan]                 : Copy shell command (mkdir/touch) to clipboard\n"
            "  [bold cyan]Ctrl+R[/bold cyan]                 : Reset editor to default starter template\n"
            "  [bold cyan]F1[/bold cyan] / [bold cyan]?[/bold cyan]                      : Toggle this help dialog\n"
            "  [bold cyan]Ctrl+C[/bold cyan] / [bold cyan]Q[/bold cyan]                  : Quit tree-tui\n\n"
            "[dim]Press Escape, F1, or ? to close[/dim]"
        )
        yield Static(help_text, id="help-dialog")


class TreeTuiApp(App[None]):
    """Interactive outline-to-tree editor and generator."""

    CSS_PATH = Path("styles.tcss")
    TITLE = "tree-tui"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+y", "copy_tree", "Copy Tree", show=True),
        Binding("ctrl+b", "copy_tree", "Copy Tree", show=False),
        Binding("ctrl+g", "copy_cmd", "Copy Shell", show=True),
        Binding("ctrl+r", "reset_template", "Reset", show=True),
        Binding("f1", "help", "Help", show=True),
        Binding("?", "help", "Help", show=False),
    ]

    def __init__(self, initial_text: str = DEFAULT_TEMPLATE) -> None:
        super().__init__()
        self.initial_text = initial_text
        self.last_rendered_tree: str = ""
        self.last_shell_cmd: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="editor-pane"):
                yield TextArea(self.initial_text, id="editor")
            with Vertical(id="preview-pane"):
                yield Static("", id="preview")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        editor = self.query_one("#editor", TextArea)
        self._update_preview(editor.text)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self._update_preview(event.text_area.text)

    def _update_preview(self, text: str) -> None:
        preview = self.query_one("#preview", Static)
        status_bar = self.query_one("#status-bar", Static)

        try:
            root = parse_outline(text)
            rendered = render_tree(root, glyphs=GLYPHS_UNICODE)
            cmd = generate_shell_command(root, one_liner=False)

            self.last_rendered_tree = rendered
            self.last_shell_cmd = cmd
            preview.update(rendered)
            status_bar.update("[green]Valid outline[/green]")
        except ValueError as e:
            status_bar.update(f"[red]Syntax Error: {e}[/red]")

    def action_copy_tree(self) -> None:
        try:
            copy_to_clipboard(self.last_rendered_tree)
            self.notify("Tree diagram copied to clipboard!", title="Clipboard")
        except ClipboardError as e:
            self.notify(f"Clipboard error: {e}", severity="error", title="Clipboard")

    def action_copy_cmd(self) -> None:
        try:
            copy_to_clipboard(self.last_shell_cmd)
            self.notify("Shell commands copied to clipboard!", title="Clipboard")
        except ClipboardError as e:
            self.notify(f"Clipboard error: {e}", severity="error", title="Clipboard")

    def action_reset_template(self) -> None:
        editor = self.query_one("#editor", TextArea)
        editor.text = DEFAULT_TEMPLATE
        self._update_preview(DEFAULT_TEMPLATE)
        self.notify("Editor reset to default template.", title="Reset")

    def action_help(self) -> None:
        self.push_screen(HelpScreen())
