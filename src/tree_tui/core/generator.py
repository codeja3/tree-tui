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

    # In outlines, root acts as the container context whose children are generated
    for child in root.children:
        collect(child, "")

    # Prune redundant parent directories if their descendant subdirectories or direct files are created
    # Leaf empty directories must be retained. Also ensure every directory path needed is covered.
    # Specifically: if dir2/subdir is created, dir2 is automatically created by mkdir -p dir2/subdir.
    # And if dir1 has only files (or files directly inside), dir1 is created with mkdir -p dir1.
    # Group directories:
    # 1) Any directory with children that are files needs mkdir -p <dir>
    # 2) Any leaf directory (no children) needs mkdir -p <dir>
    # Collect all leaf or deepest needed dir paths:
    needed_dirs: OrderedDict[str, None] = OrderedDict()

    # Find which directories directly contain files
    dirs_with_files = {p.rsplit("/", 1)[0] for p in files_to_touch if "/" in p}

    # Find all directories that have no subdirectory children
    dir_set = set(raw_dirs)
    subdirs_with_children = {p.rsplit("/", 1)[0] for p in raw_dirs if "/" in p}
    leaf_dirs = dir_set - subdirs_with_children

    for d in raw_dirs:
        # Keep if leaf directory or directly contains files
        if d in leaf_dirs or d in dirs_with_files:
            # Further optimize: if a deeper directory starts with f"{d}/", mkdir -p of the deeper covers it
            needed_dirs[d] = None

    # Filter out prefixes covered by deeper dirs
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
