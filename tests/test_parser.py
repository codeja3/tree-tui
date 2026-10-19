import pytest

from tree_tui.core.model import NodeType
from tree_tui.core.parser import parse_outline


def test_standard_2_space_indentation():
    text = """root
  child1
    grandchild1
  child2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[0].children[0].name == "grandchild1"
    assert result.children[1].name == "child2"


def test_standard_4_space_indentation():
    text = """root
    child1
        grandchild1
    child2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[0].children[0].name == "grandchild1"
    assert result.children[1].name == "child2"


def test_tab_delimited_indentation():
    text = """root
	child1
		child1_1
	child2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[0].children[0].name == "child1_1"
    assert result.children[1].name == "child2"


def test_bullet_stripping():
    text = """root
- child1
- child2
- child3"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 3
    assert result.children[0].name == "child1"
    assert result.children[1].name == "child2"
    assert result.children[2].name == "child3"


def test_marker_with_trailing_slash():
    text = """root
- dir1/
  * file.txt"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].node_type == NodeType.DIRECTORY
    assert result.children[0].name == "dir1"
    assert result.children[1].node_type == NodeType.FILE
    assert result.children[1].name == "file.txt"


def test_tree_diagram_prefix_stripping():
    text = """root
|-- child1
|   |-- grandchild1
└── child2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[0].children[0].name == "grandchild1"
    assert result.children[1].name == "child2"


def test_trailing_slash_behavior():
    text = """root/
  child1/
    grandchild1.txt"""
    result = parse_outline(text)
    assert result.name == "root"
    assert result.node_type == NodeType.DIRECTORY
    assert len(result.children) == 1
    assert result.children[0].name == "child1"
    assert result.children[0].node_type == NodeType.DIRECTORY
    assert result.children[0].children[0].name == "grandchild1.txt"
    assert result.children[0].children[0].node_type == NodeType.FILE


def test_empty_lines_and_whitespace_ignored():
    text = """root

  child1

    grandchild1

  child2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[0].children[0].name == "grandchild1"
    assert result.children[1].name == "child2"


def test_comment_lines_ignored():
    text = """root
# this is a comment
  child1
# another comment
  child2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[1].name == "child2"


def test_multi_root_returns_implicit_virtual_root():
    text = """child1
child2"""
    result = parse_outline(text)
    assert result.name == ""
    assert result.node_type == NodeType.DIRECTORY
    assert len(result.children) == 2
    assert result.children[0].name == "child1"
    assert result.children[1].name == "child2"


def test_single_root_returns_single_root_node():
    text = """root
  child1"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 1
    assert result.children[0].name == "child1"


def test_invalid_indentation_jumps_raises_value_error():
    text = """root
    child1
          grandchild1"""
    with pytest.raises(ValueError):
        parse_outline(text)


def test_list_marker_with_numbering():
    text = """root
1. item1
  2. item2"""
    result = parse_outline(text)
    assert result.name == "root"
    assert len(result.children) == 2
    assert result.children[0].name == "item1"
    assert result.children[1].name == "item2"


def test_complex_case_with_mixed_markers():
    text = """root/
- dir1/
  * file1.txt
    + nested/
      1. inner.txt"""
    result = parse_outline(text)
    assert result.name == "root"
    assert result.node_type == NodeType.DIRECTORY
    assert len(result.children) == 2
    assert result.children[0].name == "dir1"
    assert result.children[0].node_type == NodeType.DIRECTORY
    assert result.children[1].name == "file1.txt"
    assert result.children[1].node_type == NodeType.FILE
