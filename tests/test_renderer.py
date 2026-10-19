from tree_tui.core.model import NodeType, TreeNode
from tree_tui.core.renderer import GLYPHS_ASCII, GLYPHS_UNICODE, TreeGlyphs, render_tree


def test_unicode_glyph_rendering():
    """Test Unicode glyph rendering"""
    glyphs = TreeGlyphs(
        branch="├── ",
        last_branch="└── ",
        vertical="│   ",
        space="    ",
    )

    assert glyphs.branch == "├── "
    assert glyphs.last_branch == "└── "
    assert glyphs.vertical == "│   "
    assert glyphs.space == "    "


def test_ascii_glyph_rendering():
    """Test ASCII glyph rendering"""
    glyphs = TreeGlyphs(
        branch="|-- ",
        last_branch="`-- ",
        vertical="|   ",
        space="    ",
    )

    assert glyphs.branch == "|-- "
    assert glyphs.last_branch == "`-- "
    assert glyphs.vertical == "|   "
    assert glyphs.space == "    "


def test_single_node_tree():
    """Test single node tree (just root name)"""
    root = TreeNode("root", node_type=NodeType.DIRECTORY)
    result = render_tree(root, glyphs=GLYPHS_UNICODE)
    assert result == "root/"


def test_flat_list_of_children():
    """Test flat list of children"""
    root = TreeNode("root", node_type=NodeType.DIRECTORY)
    child1 = TreeNode("child1.txt", node_type=NodeType.FILE)
    child2 = TreeNode("child2.txt", node_type=NodeType.FILE)

    root.add_child(child1)
    root.add_child(child2)

    result = render_tree(root, glyphs=GLYPHS_UNICODE)
    expected = "root/\n├── child1.txt\n└── child2.txt"
    assert result == expected


def test_multi_level_nested_subtrees():
    """Test multi-level nested subtrees with correct ancestor branch vertical pipes"""
    root = TreeNode("root", node_type=NodeType.DIRECTORY)
    level1 = TreeNode("level1", node_type=NodeType.DIRECTORY)
    level2 = TreeNode("level2", node_type=NodeType.DIRECTORY)
    file1 = TreeNode("file.txt", node_type=NodeType.FILE)

    level2.add_child(file1)
    level1.add_child(level2)
    root.add_child(level1)

    result = render_tree(root, glyphs=GLYPHS_UNICODE)
    expected = "root/\n└── level1/\n    └── level2/\n        └── file.txt"
    assert result == expected


def test_virtual_root_rendering():
    """Test virtual root rendering (empty root name)"""
    root = TreeNode("", node_type=NodeType.DIRECTORY)
    child1 = TreeNode("child1.txt", node_type=NodeType.FILE)
    child2 = TreeNode("child2.txt", node_type=NodeType.FILE)

    root.add_child(child1)
    root.add_child(child2)

    result = render_tree(root, glyphs=GLYPHS_UNICODE)
    expected = "├── child1.txt\n└── child2.txt"
    assert result == expected


def test_directory_trailing_slash():
    """Test directory trailing slashes in rendered output"""
    root = TreeNode("root", node_type=NodeType.DIRECTORY)
    child_dir = TreeNode("subdir", node_type=NodeType.DIRECTORY)
    child_file = TreeNode("file.txt", node_type=NodeType.FILE)

    root.add_child(child_dir)
    root.add_child(child_file)

    result = render_tree(root, glyphs=GLYPHS_UNICODE)
    expected = "root/\n├── subdir/\n└── file.txt"
    assert result == expected


def test_ascii_rendering_flat_list():
    """Test ASCII rendering with flat list of children"""
    root = TreeNode("root", node_type=NodeType.DIRECTORY)
    child1 = TreeNode("child1.txt", node_type=NodeType.FILE)
    child2 = TreeNode("child2.txt", node_type=NodeType.FILE)

    root.add_child(child1)
    root.add_child(child2)

    result = render_tree(root, glyphs=GLYPHS_ASCII)
    expected = "root/\n|-- child1.txt\n`-- child2.txt"
    assert result == expected


def test_unicode_rendering_multi_level():
    """Test Unicode rendering with multi-level nested subtrees"""
    root = TreeNode("project", node_type=NodeType.DIRECTORY)
    src = TreeNode("src", node_type=NodeType.DIRECTORY)
    tests = TreeNode("tests", node_type=NodeType.DIRECTORY)
    main_py = TreeNode("main.py", node_type=NodeType.FILE)
    test_main_py = TreeNode("test_main.py", node_type=NodeType.FILE)

    src.add_child(main_py)
    tests.add_child(test_main_py)
    root.add_child(src)
    root.add_child(tests)

    result = render_tree(root, glyphs=GLYPHS_UNICODE)
    expected = "project/\n├── src/\n│   └── main.py\n└── tests/\n    └── test_main.py"
    assert result == expected
