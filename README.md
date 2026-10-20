# tree-tui

[![Python >= 3.11](https://img.shields.io/badge/python->=3.11-blue.svg)](https://www.python.org/)
[![Built with Textual](https://img.shields.io/badge/built%20with-Textual-teal.svg)](https://textual.textualize.io/)
[![Package Manager: uv](https://img.shields.io/badge/package%20manager-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)

A decoupled, high-performance terminal utility and interactive TUI for converting text outlines into canonical ASCII/Unicode tree diagrams and executable POSIX shell reproduction commands (`mkdir -p` and `touch`).

---

## Features

- **Blazing Fast (<1ms rendering budget):** Core domain engine parses and renders 1,000 lines in ~0.90ms (far exceeding the 60 FPS / 16ms interactive threshold).
- **Decoupled Architecture:** Core engine (`model`, `parser`, `renderer`, `generator`) has **zero UI dependencies** and functions as a standalone, headless Python library.
- **Interactive Dual-Pane TUI:** Built with [Textual](https://textual.textualize.io/) featuring real-time syntax checking, debounced rendering, and starter templates.
- **Flexible Ingestion:** Reads standard 2-space or 4-space indentation, tabs, Markdown bullet/numbered lists (`-`, `*`, `+`, `1.`), and pasted ASCII/Unicode diagrams (`|--`, `└──`).
- **Deterministic Shell Synthesis:** Produces clean, deduplicated, idempotent POSIX shell scripts or one-liners (`mkdir -p ... && touch ...`) with safe path escaping via `shlex.quote`.
- **Zero Heavy Clipboard Dependencies:** Dispatches directly to native OS clipboards (`pbcopy` on macOS, `wl-copy` on Wayland, `xclip`/`xsel` on X11).

---

## Installation & Setup

`tree-tui` is managed with [`uv`](https://github.com/astral-sh/uv). Ensure you have Python >= 3.11 installed.

### 1. Clone the repository
```bash
git clone https://github.com/codeja3/tree-tui.git
cd tree-tui
```

### 2. Install dependencies with `uv`
```bash
# Sync runtime and dev dependencies
uv sync --all-extras
```

---

## Usage

### 1. Interactive TUI Mode
Launching `tree-tui` directly in an interactive terminal opens the full-screen dual-pane editor:

```bash
uv run tree-tui
```

#### TUI Keyboard Shortcuts:
| Keybinding | Action |
| :--- | :--- |
| `Ctrl+Y` or `Ctrl+B` | Copy rendered tree diagram to clipboard |
| `Ctrl+G` | Copy generated shell command (`mkdir`/`touch`) to clipboard |
| `Ctrl+R` | Reset editor pane to default starter template |
| `F1` or `?` | Toggle Help & Keybindings Modal dialog |
| `Ctrl+C` or `Q` | Quit `tree-tui` |

---

### 2. Headless CLI Mode

#### Render Tree from an Outline File
```bash
uv run tree-tui path/to/outline.txt
```

#### Render Tree from Piped STDIN
```bash
cat << 'EOF' | uv run tree-tui
src/
  tree_tui/
    core/
      parser.py
      renderer.py
tests/
  test_parser.py
EOF
```

Output:
```text
src/
└── tree_tui/
    └── core/
        ├── parser.py
        └── renderer.py
tests/
└── test_parser.py
```

#### ASCII Mode (`--ascii` / `-a`)
Generate standard 7-bit ASCII trees suitable for plain text emails or code comments:
```bash
uv run tree-tui --ascii path/to/outline.txt
```

Output:
```text
root/
|-- dir1/
|   `-- file.txt
`-- dir2/
```

#### Shell Command Synthesis (`-c` / `--generate-command`)
Synthesize executable shell commands to construct the directory structure:
```bash
uv run tree-tui -c path/to/outline.txt
```

Output:
```bash
mkdir -p dir1 dir2
touch dir1/file.txt
```

#### One-Liner Shell Chain (`--one-liner`)
```bash
uv run tree-tui -c --one-liner path/to/outline.txt
```

Output:
```bash
mkdir -p dir1 dir2 && touch dir1/file.txt
```

---

## Python API Usage

You can use the core domain engine directly in your own Python scripts without any TUI or terminal dependencies:

```python
from tree_tui.core.parser import parse_outline
from tree_tui.core.renderer import render_tree, GLYPHS_UNICODE, GLYPHS_ASCII
from tree_tui.core.generator import generate_shell_command

outline = """
app/
  models/
    user.py
  views/
    index.html
"""

# Parse outline into canonical TreeNode hierarchy
root = parse_outline(outline)

# Render ASCII / Unicode diagram
print(render_tree(root, glyphs=GLYPHS_UNICODE))

# Generate POSIX command
cmd = generate_shell_command(root, one_liner=True)
print(cmd)
# Output: mkdir -p app/models app/views && touch app/models/user.py app/views/index.html
```

---

## Development & Verification

All quality checks and tests are verified through `uv`:

```bash
# Run unit, integration, and pilot tests
uv run pytest

# Run tests with coverage report (target >= 90%)
uv run pytest --cov=tree_tui --cov-report=term-missing

# Run performance benchmark (<16ms budget enforcement)
uv run pytest tests/test_perf.py

# Lint and formatting checks
uv run ruff check src tests

# Static type checking (100% type annotations)
uv run mypy src tests
```

---

## Project Architecture

```
tree-tui/
├── pyproject.toml              # Build & dependency metadata (Hatchling)
├── README.md                   # Project documentation & run guide
├── SPEC.md                     # Technical specification contract
├── PRD.md                      # Product requirements document
├── AGENTS.md                   # Engineering standards for AI & humans
├── TODO.md                     # SDD / TDD phase completion log
├── src/
│   └── tree_tui/
│       ├── cli.py              # CLI entry point and argument parsing
│       ├── core/               # Pure domain engine (Zero UI dependencies)
│       │   ├── model.py        # Canonical TreeNode data structures
│       │   ├── parser.py       # Outline & indentation parser
│       │   ├── renderer.py     # ASCII / Unicode tree string renderer
│       │   └── generator.py    # POSIX shell command synthesis
│       ├── platform/
│       │   └── clipboard.py    # Zero-dependency OS clipboard dispatch
│       └── tui/
│           ├── app.py          # Interactive Textual TUI application
│           └── styles.tcss     # TUI styling & responsive layout
└── tests/                      # 100% test coverage suite
    ├── test_cli.py
    ├── test_clipboard.py
    ├── test_generator.py
    ├── test_model.py
    ├── test_parser.py
    ├── test_perf.py
    ├── test_renderer.py
    └── test_tui.py
```
---

## License

Apache License 2.0. See project files for details.

---

Built with qwen3-coder:30b on Ollama and Gemini-3.8-Flash as a reviewer. 
