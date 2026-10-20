import time

from tree_tui.core.generator import generate_shell_command
from tree_tui.core.parser import parse_outline
from tree_tui.core.renderer import render_tree


def generate_synthetic_outline(num_lines: int = 1000, max_depth: int = 10) -> str:
    lines = []
    for i in range(num_lines):
        depth = i % max_depth
        indent = "  " * depth
        lines.append(f"{indent}item_{i}")
    return "\n".join(lines)

def test_parser_and_renderer_perf_budget():
    text = generate_synthetic_outline(1000, 10)
    
    # Warm up
    for _ in range(2):
        root = parse_outline(text)
        render_tree(root)
    
    # Measure performance
    times = []
    for _ in range(5):
        start_time = time.perf_counter()
        root = parse_outline(text)
        render_tree(root)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    assert avg_time < 0.016, f"Average time {avg_time:.4f}s exceeded 16ms budget"

def test_generator_perf_budget():
    text = generate_synthetic_outline(1000, 10)
    root = parse_outline(text)
    
    # Warm up
    for _ in range(2):
        generate_shell_command(root)
    
    # Measure performance
    times = []
    for _ in range(5):
        start_time = time.perf_counter()
        generate_shell_command(root)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    avg_time = sum(times) / len(times)
    assert avg_time < 0.016, f"Average time {avg_time:.4f}s exceeded 16ms budget"
