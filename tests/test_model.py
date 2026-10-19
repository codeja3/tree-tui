from tree_tui.core.model import NodeType, TreeNode


def test_tree_node_creation():
    """Test TreeNode creation with name and node_type."""
    node = TreeNode(name="test", node_type=NodeType.FILE)
    assert node.name == "test"
    assert node.node_type == NodeType.FILE
    assert node.children == []
    assert node.parent is None


def test_node_type_directory_vs_file():
    """Test NodeType.DIRECTORY vs NodeType.FILE."""
    dir_node = TreeNode(name="dir", node_type=NodeType.DIRECTORY)
    file_node = TreeNode(name="file", node_type=NodeType.FILE)

    assert dir_node.node_type == NodeType.DIRECTORY
    assert file_node.node_type == NodeType.FILE


def test_add_child_linking():
    """Test add_child linking: verify child.parent assignment and children list ordering."""
    parent = TreeNode(name="parent", node_type=NodeType.DIRECTORY)
    child1 = TreeNode(name="child1", node_type=NodeType.FILE)
    child2 = TreeNode(name="child2", node_type=NodeType.DIRECTORY)

    parent.add_child(child1)
    parent.add_child(child2)

    assert child1.parent == parent
    assert child2.parent == parent
    assert parent.children == [child1, child2]


def test_is_dir_property_explicit_directory():
    """Test is_dir property: explicitly directory."""
    dir_node = TreeNode(name="dir", node_type=NodeType.DIRECTORY)
    assert dir_node.is_dir is True


def test_is_dir_property_file():
    """Test is_dir property: explicitly file."""
    file_node = TreeNode(name="file", node_type=NodeType.FILE)
    assert file_node.is_dir is False


def test_is_dir_property_implicit_directory():
    """Test is_dir property: file becoming implicitly directory when children exist."""
    file_node = TreeNode(name="file", node_type=NodeType.FILE)
    child = TreeNode(name="child", node_type=NodeType.FILE)

    assert file_node.is_dir is False

    file_node.add_child(child)
    assert file_node.is_dir is True


def test_nested_hierarchy_traversal():
    """Test nested hierarchy traversal."""
    root = TreeNode(name="root", node_type=NodeType.DIRECTORY)
    dir1 = TreeNode(name="dir1", node_type=NodeType.DIRECTORY)
    dir2 = TreeNode(name="dir2", node_type=NodeType.DIRECTORY)
    file1 = TreeNode(name="file1", node_type=NodeType.FILE)

    root.add_child(dir1)
    root.add_child(dir2)
    dir1.add_child(file1)

    # Traverse ancestors
    assert file1.parent == dir1
    assert dir1.parent == root
    assert root.parent is None

    # Check children hierarchy
    assert root.children == [dir1, dir2]
    assert dir1.children == [file1]


def test_path_calculation():
    """Test path calculation through ancestor traversal."""
    root = TreeNode(name="root", node_type=NodeType.DIRECTORY)
    dir1 = TreeNode(name="dir1", node_type=NodeType.DIRECTORY)
    file1 = TreeNode(name="file1", node_type=NodeType.FILE)

    root.add_child(dir1)
    dir1.add_child(file1)

    # Build path from file to root
    path_parts = []
    current = file1
    while current is not None:
        path_parts.append(current.name)
        current = current.parent

    assert path_parts == ["file1", "dir1", "root"]
