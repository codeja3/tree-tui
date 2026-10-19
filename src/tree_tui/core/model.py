from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    DIRECTORY = "directory"
    FILE = "file"


@dataclass(slots=True)
class TreeNode:
    name: str
    node_type: NodeType
    children: list[TreeNode] = field(default_factory=list)
    parent: TreeNode | None = field(default=None, repr=False)

    def add_child(self, child: TreeNode) -> None:
        child.parent = self
        self.children.append(child)

    @property
    def is_dir(self) -> bool:
        return self.node_type == NodeType.DIRECTORY or len(self.children) > 0
