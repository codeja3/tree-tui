from tree_tui.core.generator import generate_shell_command
from tree_tui.core.model import NodeType, TreeNode


def test_pure_directory_structures():
    """Test pure directory structures (only mkdir -p)."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY),
        TreeNode(name="dir2", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="subdir", node_type=NodeType.DIRECTORY)
        ])
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p dir1 dir2/subdir"
    assert result == expected

def test_pure_file_structures():
    """Test pure file structures (only touch, or mkdir -p if needed)."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="file1.txt", node_type=NodeType.FILE),
        TreeNode(name="file2.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "touch file1.txt file2.txt"
    assert result == expected

def test_mixed_hierarchies():
    """Test mixed hierarchies: directories created before files are touched."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="file1.txt", node_type=NodeType.FILE)
        ]),
        TreeNode(name="file2.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p dir1\ntouch dir1/file1.txt file2.txt"
    assert result == expected

def test_parent_directory_creation_ahead_of_touch():
    """Test parent directory creation ahead of touch."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="parent", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="child", node_type=NodeType.DIRECTORY, children=[
                TreeNode(name="grandchild", node_type=NodeType.DIRECTORY, children=[
                    TreeNode(name="deep_file.txt", node_type=NodeType.FILE)
                ])
            ])
        ])
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p parent/child/grandchild\ntouch parent/child/grandchild/deep_file.txt"
    assert result == expected

def test_path_escaping_with_spaces():
    """Test path escaping with spaces or special characters using shlex.quote."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="my folder", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="my file.txt", node_type=NodeType.FILE)
        ])
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p 'my folder'\ntouch 'my folder/my file.txt'"
    assert result == expected

def test_path_escaping_with_special_characters():
    """Test path escaping with special characters."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="folder with & special chars", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="file with $pecial.txt", node_type=NodeType.FILE)
        ])
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p 'folder with & special chars'\ntouch 'folder with & special chars/file with $pecial.txt'"
    assert result == expected

def test_leaf_empty_directory_retention():
    """Test leaf empty directory retention (ensuring empty directories are in mkdir -p)."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="empty_dir", node_type=NodeType.DIRECTORY),
        TreeNode(name="file.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p empty_dir\ntouch file.txt"
    assert result == expected

def test_one_liner_format():
    """Test one_liner=True format (mkdir -p ... && touch ...)."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY),
        TreeNode(name="file.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=True)
    expected = "mkdir -p dir1 && touch file.txt"
    assert result == expected

def test_multiline_format():
    """Test one_liner=False format (multi-line separated by newline)."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY),
        TreeNode(name="file.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p dir1\ntouch file.txt"
    assert result == expected

def test_virtual_root_handling():
    """Test virtual root handling (root.name == "")."""
    tree = TreeNode(name="", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY),
        TreeNode(name="file.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p dir1\ntouch file.txt"
    assert result == expected

def test_complex_mixed_structure():
    """Test a complex mixed structure with multiple levels."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="sub1", node_type=NodeType.DIRECTORY, children=[
                TreeNode(name="file1.txt", node_type=NodeType.FILE)
            ]),
            TreeNode(name="file2.txt", node_type=NodeType.FILE)
        ]),
        TreeNode(name="dir2", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="file3.txt", node_type=NodeType.FILE)
        ]),
        TreeNode(name="root_file.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=False)
    expected = "mkdir -p dir1/sub1 dir2\ntouch dir1/sub1/file1.txt dir1/file2.txt dir2/file3.txt root_file.txt"
    assert result == expected

def test_complex_one_liner_format():
    """Test complex structure with one_liner=True."""
    tree = TreeNode(name="root", node_type=NodeType.DIRECTORY, children=[
        TreeNode(name="dir1", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="file1.txt", node_type=NodeType.FILE)
        ]),
        TreeNode(name="dir2", node_type=NodeType.DIRECTORY, children=[
            TreeNode(name="file2.txt", node_type=NodeType.FILE)
        ]),
        TreeNode(name="root_file.txt", node_type=NodeType.FILE)
    ])
    
    result = generate_shell_command(tree, one_liner=True)
    expected = "mkdir -p dir1 dir2 && touch dir1/file1.txt dir2/file2.txt root_file.txt"
    assert result == expected
