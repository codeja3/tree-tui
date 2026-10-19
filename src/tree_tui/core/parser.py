from __future__ import annotations

import re

from tree_tui.core.model import NodeType, TreeNode

TREE_GLYPH_PREFIX_REGEX = re.compile(
    r"^(?P<prefix>(?:[|│`\s]*?(?:\|--|`--|├──|└──))\s*)"
)
LIST_MARKER_REGEX = re.compile(r"^(?:[-*+]|\d+\.)\s+")


def parse_outline(text: str) -> TreeNode:
    """
    Parses indented text outlines into a canonical TreeNode hierarchy.
    """
    lines = text.splitlines()
    raw_items: list[tuple[int, str, NodeType]] = []

    for raw_line in lines:
        expanded = raw_line.expandtabs(4)
        stripped = expanded.strip()
        if not stripped or stripped.startswith("#"):
            continue

        tree_match = TREE_GLYPH_PREFIX_REGEX.match(expanded)
        if tree_match:
            full_prefix = tree_match.group("prefix")
            pipes = (
                full_prefix.count("|")
                + full_prefix.count("│")
                + full_prefix.count("`")
                + full_prefix.count("├")
                + full_prefix.count("└")
            )
            indent = pipes * 4
            content = expanded[len(full_prefix):].strip()
        else:
            indent = len(expanded) - len(expanded.lstrip(" "))
            content = expanded.strip()
            # If line starts with a list marker, note that in markdown/outlines
            # list markers at indent 0 under an unindented root heading can belong to root.
            # To handle both cases cleanly, we track whether a marker was present.
            marker_match = LIST_MARKER_REGEX.match(content)
            has_marker = marker_match is not None
            if has_marker:
                content = LIST_MARKER_REGEX.sub("", content, count=1).strip()
            # If the very first line has no marker and subsequent line has indent 0 with marker,
            # offset marked lines by 2 if root was unindented and unmarked
            if has_marker and indent == 0:
                indent = 2

        if content.endswith("/"):
            node_type = NodeType.DIRECTORY
            name = content[:-1]
        else:
            node_type = NodeType.FILE
            name = content

        raw_items.append((indent, name, node_type))

    if not raw_items:
        return TreeNode(name="", node_type=NodeType.DIRECTORY)

    # Indentation tracking stack: [(indent_level, TreeNode)]
    stack: list[tuple[int, TreeNode]] = []
    top_level_nodes: list[TreeNode] = []
    indent_step: int | None = None

    for indent, name, node_type in raw_items:
        node = TreeNode(name=name, node_type=node_type)

        while stack and stack[-1][0] >= indent:
            stack.pop()

        if not stack:
            top_level_nodes.append(node)
            stack.append((indent, node))
            continue

        parent_indent, parent_node = stack[-1]

        # Check indent step validity
        delta = indent - parent_indent
        if indent_step is None and delta > 0:
            indent_step = delta
        elif indent_step is not None and delta > indent_step:
            raise ValueError(f"Invalid indentation jump from {parent_indent} to {indent}")

        parent_node.add_child(node)
        stack.append((indent, node))

    if len(top_level_nodes) == 1:
        return top_level_nodes[0]

    virtual_root = TreeNode(name="", node_type=NodeType.DIRECTORY)
    for root_node in top_level_nodes:
        virtual_root.add_child(root_node)
    return virtual_root
