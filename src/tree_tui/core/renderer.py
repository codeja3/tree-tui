from __future__ import annotations

from dataclasses import dataclass

from tree_tui.core.model import TreeNode


@dataclass(frozen=True)
class TreeGlyphs:
    branch: str = "├── "
    last_branch: str = "└── "
    vertical: str = "│   "
    space: str = "    "


GLYPHS_UNICODE = TreeGlyphs()
GLYPHS_ASCII = TreeGlyphs(branch="|-- ", last_branch="`-- ", vertical="|   ", space="    ")


def render_tree(root: TreeNode, glyphs: TreeGlyphs = GLYPHS_UNICODE) -> str:
    if not root.children:
        if root.name == "":
            return ""
        return f"{root.name}/" if root.is_dir and not root.name.endswith("/") else root.name

    # Handle virtual root (empty name)
    if root.name == "":
        virtual_lines: list[str] = []
        for i, child in enumerate(root.children):
            is_last = i == len(root.children) - 1
            virtual_lines.append(_render_node(child, glyphs, is_last=is_last))
        return "\n".join(virtual_lines)

    # Regular root node
    root_lines: list[str] = []
    name = f"{root.name}/" if root.is_dir and not root.name.endswith("/") else root.name
    root_lines.append(name)

    for i, child in enumerate(root.children):
        is_last = i == len(root.children) - 1
        root_lines.append(_render_node(child, glyphs, is_last))

    return "\n".join(root_lines)


def _render_node(node: TreeNode, glyphs: TreeGlyphs, is_last: bool, prefix: str = "") -> str:
    # Determine node name with trailing slash if directory
    node_name = f"{node.name}/" if node.is_dir and not node.name.endswith("/") else node.name

    if not node.children:
        return f"{prefix}{glyphs.last_branch if is_last else glyphs.branch}{node_name}"

    result_lines = [f"{prefix}{glyphs.last_branch if is_last else glyphs.branch}{node_name}"]

    # Add children with proper prefixes
    for i, child in enumerate(node.children):
        child_is_last = i == len(node.children) - 1
        child_prefix = prefix + (glyphs.space if is_last else glyphs.vertical)
        result_lines.append(_render_node(child, glyphs, child_is_last, child_prefix))

    return "\n".join(result_lines)
