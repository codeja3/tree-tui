from __future__ import annotations

import argparse
import sys

from tree_tui.core.generator import generate_shell_command
from tree_tui.core.parser import parse_outline
from tree_tui.core.renderer import GLYPHS_ASCII, GLYPHS_UNICODE, render_tree


def _launch_tui() -> None:
    from tree_tui.tui.app import TreeTuiApp

    app = TreeTuiApp()
    app.run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tree-tui",
        description="Render tree outlines from files, stdin, or interactive TUI.",
    )
    parser.add_argument("file", nargs="?", type=str, help="Input file path")
    parser.add_argument("-a", "--ascii", action="store_true", help="Use ASCII characters for tree rendering")
    parser.add_argument("-c", "--generate-command", action="store_true", help="Generate shell commands")
    parser.add_argument("--one-liner", action="store_true", help="Combine commands in one line")
    parser.add_argument("-t", "--text", type=str, help="Raw outline text")

    args = parser.parse_args(argv)

    content: str
    if args.file:
        try:
            with open(args.file) as f:
                content = f.read()
        except (FileNotFoundError, OSError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    elif args.text:
        content = args.text
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        _launch_tui()
        return 0

    try:
        root = parse_outline(content)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.generate_command:
        command = generate_shell_command(root, one_liner=args.one_liner)
        print(command)
        return 0

    glyphs = GLYPHS_ASCII if args.ascii else GLYPHS_UNICODE
    output = render_tree(root, glyphs=glyphs)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
