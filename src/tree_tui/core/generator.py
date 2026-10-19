from __future__ import annotations

import shlex
from collections import OrderedDict

from tree_tui.core.model import NodeType, TreeNode


def generate_shell_command(root: TreeNode, one_liner: bool = False) -> str:
    """
    Generates POSIX shell commands (mkdir -p / touch) to reproduce the directory tree.
    """
    if not root.children:
        if root.name and root.node_type == NodeType.DIRECTORY:
            return f"mkdir -p {shlex.quote(root.name)}"
        elif root.name and root.node_type == NodeType.FILE:
            return f"touch {shlex.quote(root.name)}"
        return ""

    raw_dirs: list[str] = []
    files_to_touch: list[str] = []

    def collect(node: TreeNode, current_prefix: str) -> None:
        path = f"{current_prefix}/{node.name}" if current_prefix else node.name

        if node.is_dir:
            raw_dirs.append(path)
            for child in node.children:
                collect(child, path)
        else:
            files_to_touch.append(path)

    for child in root.children:
        collect(child, "")

    # Prune redundant parent directories if their descendant subdirectories or direct files are created
    needed_dirs: OrderedDict[str, None] = OrderedDict()

    # Find which directories directly contain files
    dirs_with_files = {p.rsplit("/", 1)[0] for p in files_to_touch if "/" in p}

    # Find all directories that have no subdirectory children
    dir_set = set(raw_dirs)
    subdirs_with_children = {p.rsplit("/", 1)[0] for p in raw_dirs if "/" in p}
    leaf_dirs = dir_set - subdirs_with_children

    for d in raw_dirs:
        if d in leaf_dirs or d in dirs_with_files:
            needed_dirs[d] = None

    all_needed = list(needed_dirs.keys())
    final_dirs: list[str] = []
    for d in all_needed:
        if not any(other != d and other.startswith(f"{d}/") for other in all_needed):
            final_dirs.append(d)

    commands: list[str] = []

    if final_dirs:
        quoted_dirs = [shlex.quote(d) for d in final_dirs]
        commands.append(f"mkdir -p {' '.join(quoted_dirs)}")

    if files_to_touch:
        quoted_files = [shlex.quote(f) for f in files_to_touch]
        commands.append(f"touch {' '.join(quoted_files)}")

    if not commands:
        return ""

    separator = " && " if one_liner else "\n"
    return separator.join(commands)
