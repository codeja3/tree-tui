# TODO.md: tree-tui Implementation & TDD Task List Contract

This document is the actionable task contract for developing `tree-tui`. It breaks down the specifications in [SPEC.md](SPEC.md), [PRD.md](PRD.md), and [AGENTS.md](AGENTS.md) into atomic, test-driven phases.

## Execution Rules for the Coding Agent
1. **Red-Green-Refactor:** Always write or verify failing tests first (`uv run pytest`) before writing implementation logic.
2. **Atomic Commits / Verification:** Complete one sub-task at a time and ensure all existing tests pass before checking off a box.
3. **Decoupled Architecture:** Keep `tree_tui.core.*` completely free of UI/TUI dependencies (`textual`, `rich`).
4. **Environment:** Use `uv` for all commands (`uv run pytest`, `uv add`, etc.). Python target is `>= 3.11`.

---

## Phase 1: Project Scaffolding & Toolchain Setup
- [x] **Task 1.1: Project initialization with `uv`**
  - Create `pyproject.toml` targeting Python `>= 3.11` using the `hatchling` build backend.
  - Configure dependencies: `textual>=0.70.0`.
  - Configure dev/test dependencies: `pytest`, `pytest-benchmark`, `pytest-cov`, `ruff`, `mypy`.
  - Configure CLI entry point script `tree-tui = "tree_tui.cli:main"`.
  - Initialize project directory structure (`src/tree_tui/core`, `src/tree_tui/platform`, `src/tree_tui/tui`, `tests`).
- [x] **Task 1.2: Base Environment Verification**
  - Run `uv sync` to generate `uv.lock` and install virtual environment.
  - Verify `uv run pytest` runs cleanly on an empty/placeholder test suite.

---

## Phase 2: Core Domain Model (`tree_tui.core.model`)
- [x] **Task 2.1: Write tests in `tests/test_model.py`**
  - Test `TreeNode` creation (name, `node_type`).
  - Test `NodeType.DIRECTORY` vs `NodeType.FILE`.
  - Test `add_child` linking: check `child.parent` assignment and `children` list ordering.
  - Test `is_dir` property: explicitly directory vs implicitly directory when children exist.
  - Test nested hierarchy traversal and path calculation.
- [x] **Task 2.2: Implement `src/tree_tui/core/model.py`**
  - Implement `NodeType` enum.
  - Implement `@dataclass TreeNode` with slots for performance.
  - Implement `add_child(self, child: TreeNode) -> None`.
  - Implement `is_dir` computed property.
  - Verify all tests pass with `uv run pytest tests/test_model.py`.

---

## Phase 3: Outline & Indentation Parser (`tree_tui.core.parser`)
- [ ] **Task 3.1: Write tests in `tests/test_parser.py`**
  - Test standard 2-space and 4-space indentation.
  - Test tab-delimited indentation (`\t`).
  - Test bullet/marker stripping (`- `, `* `, `+ `, `1. `).
  - Test tree diagram prefix stripping (e.g., lines starting with `|-- `, `└── `, `│   `).
  - Test trailing slash behavior (`folder/` sets `NodeType.DIRECTORY`).
  - Test empty lines and whitespace lines (ignored).
  - Test comment lines starting with `#` (ignored).
  - Test multi-root outline (returns implicit virtual root).
  - Test invalid indentation jumps (raise `ValueError`).
- [ ] **Task 3.2: Implement `src/tree_tui/core/parser.py`**
  - Implement `parse_outline(text: str) -> TreeNode` using an indent-tracking stack.
  - Normalize tab stops (default 4 spaces).
  - Support list marker stripping while accurately counting prefix indent levels.
  - Verify all tests pass with `uv run pytest tests/test_parser.py`.

---

## Phase 4: ASCII / Unicode Tree Renderer (`tree_tui.core.renderer`)
- [ ] **Task 4.1: Write tests in `tests/test_renderer.py`**
  - Test Unicode glyph rendering (`├── `, `└── `, `│   `, `    `).
  - Test ASCII glyph rendering (`|-- `, `` `-- ``, `|   `, `    `).
  - Test single node tree (just root name).
  - Test flat list of children (last child gets `└── `, others get `├── `).
  - Test multi-level nested subtrees with correct ancestor branch vertical pipes.
  - Test virtual root rendering (children rendered without top-level wrapper name).
  - Test directory trailing slashes in rendered output.
- [ ] **Task 4.2: Implement `src/tree_tui/core/renderer.py`**
  - Implement `TreeGlyphs` dataclass with `GLYPHS_UNICODE` and `GLYPHS_ASCII` presets.
  - Implement recursive or stack-based `render_tree(root: TreeNode, glyphs: TreeGlyphs = GLYPHS_UNICODE) -> str`.
  - Verify all tests pass with `uv run pytest tests/test_renderer.py`.

---

## Phase 5: Shell Command Generator (`tree_tui.core.generator`)
- [ ] **Task 5.1: Write tests in `tests/test_generator.py`**
  - Test generation of `mkdir -p` for pure directory structures.
  - Test generation of `touch` for file paths.
  - Test parent directory creation ahead of `touch` (or combined `mkdir -p && touch`).
  - Test path escaping with spaces or special characters using `shlex.quote`.
  - Test leaf empty directory retention.
  - Test one-liner format (`mkdir -p ... && touch ...`) vs multi-line format.
- [ ] **Task 5.2: Implement `src/tree_tui/core/generator.py`**
  - Implement path collection by walking `TreeNode`.
  - Group directories and files into clean, deduplicated POSIX shell commands.
  - Implement `generate_shell_command(root: TreeNode, one_liner: bool = False) -> str`.
  - Verify all tests pass with `uv run pytest tests/test_generator.py`.

---

## Phase 6: Platform Clipboard Integration (`tree_tui.platform.clipboard`)
- [ ] **Task 6.1: Write tests in `tests/test_clipboard.py`**
  - Mock platform binaries (`pbcopy`, `wl-copy`, `xclip`, `xsel`).
  - Test macOS clipboard execution (`pbcopy`).
  - Test Linux Wayland clipboard execution (`wl-copy`).
  - Test Linux X11 clipboard execution (`xclip`/`xsel`).
  - Test graceful fallback when no clipboard utility is installed (`ClipboardError`).
- [ ] **Task 6.2: Implement `src/tree_tui/platform/clipboard.py`**
  - Detect platform and locate executable binary via `shutil.which`.
  - Implement `copy_to_clipboard(text: str) -> None`.
  - Verify all tests pass with `uv run pytest tests/test_clipboard.py`.

---

## Phase 7: CLI Controller (`tree_tui.cli`)
- [ ] **Task 7.1: Write tests in `tests/test_cli.py`**
  - Test reading outline from STDIN (`sys.stdin`).
  - Test reading outline from file path argument (`tree-tui outline.txt`).
  - Test ASCII mode flag (`--ascii`).
  - Test shell command generator flag (`-c`, `--generate-command`).
  - Test opening TUI mode when run with no piped input and no file argument.
- [ ] **Task 7.2: Implement `src/tree_tui/cli.py`**
  - Build `argparse` CLI interface.
  - Route execution to parser, renderer, or generator based on flags.
  - Launch Textual TUI when interactive mode is detected (TTY + no pipe).
  - Verify all tests pass with `uv run pytest tests/test_cli.py`.

---

## Phase 8: Interactive TUI Application (`tree_tui.tui`)
- [ ] **Task 8.1: Write TUI pilot tests in `tests/test_tui.py`**
  - Use `textual.pilot` to test app launch without a live terminal.
  - Test input in `#editor` triggers update in `#preview`.
  - Test keybinding `ctrl+y` / `ctrl+b` calls clipboard copy for tree diagram.
  - Test keybinding `ctrl+g` calls clipboard copy for generated shell command.
  - Test keybinding `ctrl+r` resets editor to starter template.
  - Test syntax error handling: malformed outline displays subtle warning without crashing app.
- [ ] **Task 8.2: Implement `src/tree_tui/tui/app.py` & `styles.tcss`**
  - Create Textual `App` with `Header`, `Footer`, left `TextArea`, and right `Static`/`RichLog`.
  - Implement debounced event handler on `TextArea.Changed`.
  - Add help modal dialog (`f1` / `?`).
  - Verify all tests pass with `uv run pytest tests/test_tui.py`.

---

## Phase 9: Performance Benchmarking & Hardening
- [ ] **Task 9.1: Implement performance test in `tests/test_perf.py`**
  - Generate synthetic 1,000-line nested tree input.
  - Measure execution time of `parse_outline` + `render_tree`.
  - Assert that execution completes in `< 16ms`.
- [ ] **Task 9.2: Code Quality, Linting, & Type Checking**
  - Run `uv run ruff check src tests`.
  - Run `uv run mypy src`.
  - Verify 100% full test suite pass: `uv run pytest --cov=tree_tui`.
