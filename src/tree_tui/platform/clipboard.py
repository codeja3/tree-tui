from __future__ import annotations

import shutil
import subprocess


class ClipboardError(Exception):
    """Exception raised when clipboard operation fails."""


def copy_to_clipboard(text: str) -> None:
    """
    Copy text to the system clipboard using available tools.

    Lookup order:
    1. pbcopy
    2. wl-copy
    3. xclip -selection clipboard
    4. xsel --clipboard --input
    """
    cmd: list[str] | None = None

    if shutil.which("pbcopy"):
        cmd = ["pbcopy"]
    elif shutil.which("wl-copy"):
        cmd = ["wl-copy"]
    elif shutil.which("xclip"):
        cmd = ["xclip", "-selection", "clipboard"]
    elif shutil.which("xsel"):
        cmd = ["xsel", "--clipboard", "--input"]

    if cmd is None:
        raise ClipboardError("No clipboard utility found.")

    try:
        subprocess.run(cmd, input=text.encode("utf-8"), check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        raise ClipboardError(f"Failed to copy to clipboard: {e}") from e
