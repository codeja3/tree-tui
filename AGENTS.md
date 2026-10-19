# AGENTS.md: tree-tui Engineering & AI Standards

This document defines the immutable rules of engagement for developing `tree-tui`. It governs the architectural design, engineering standards, and workflow between the developer and the AI coding agent.

## 1. Development Workflow & AI Collaboration
* **Specification-Driven Development (SDD):** `SPEC.md` and `PRD.md` are the authoritative sources of truth. Public APIs, data models, and behavioral contracts must be defined in `SPEC.md` prior to implementation.
* **Strict Test-Driven Development (TDD):** Red-Green-Refactor cycle:
  1. Write failing xUnit-style unit/integration tests in `tests/` matching contracts in `SPEC.md`.
  2. Run the test suite via CLI to verify failure.
  3. Author the minimal implementation code to pass the tests.
  4. Run tests to confirm green.
  5. Refactor for performance, readability, and adherence to clean code principles.
* **Autonomous Verification:** The agent should use CLI tools (`uv run pytest`) to verify tests, linting, and benchmarks directly.

## 2. Core Architectural & Design Principles
* **Decoupled Domain Engine:** The core engine (`tree_tui.core.*` — parser, renderer, model, generator) must remain **100% decoupled from any UI/TUI frameworks** (Textual, Rich). It must be usable as a pure Python library and tested in headless isolation.
* **Single Responsibility Principle (SRP):**
  - `model.py`: Pure hierarchical tree data structures and invariants.
  - `parser.py`: Outline/text ingestion into `TreeNode`.
  - `renderer.py`: `TreeNode` rendering into ASCII/Unicode strings.
  - `generator.py`: `TreeNode` synthesis into POSIX shell commands (`mkdir -p`, `touch`).
* **Defensive Programming & Fail-Fast:** Validate inputs, indentation levels, and tree boundaries immediately. Raise explicit exceptions rather than producing corrupted state.
* **Safety First (Zero Disk Modification):** `tree-tui` does not alter user filesystems directly when parsing outlines. Instead, it generates and outputs reproducible shell commands (`mkdir -p` / `touch`) for user review and execution.

## 3. Technology & Language Standards
* **Python Ecosystem:** Python >= 3.11.
* **Package Management:** `uv` is the mandated project and package manager (`uv sync`, `uv add`, `uv run pytest`).
* **Path Management:** `pathlib.Path` must be used for all path representations. String concatenation for paths is prohibited.
* **Type Safety:** 100% type annotations on all function signatures, methods, and classes.
* **Data Models:** Use standard Python `dataclasses` (with slots/frozen where applicable for performance).
* **Cross-Platform:** Native support for macOS and Linux. Path formatting and shell command quoting must use `shlex.quote`.

## 4. Performance & Non-Functional Mandates
* **Sub-16ms Parsing & Rendering Budget:** The parser and renderer must process 1,000 lines within < 16ms (60 FPS responsiveness for TUI keystrokes). Performance tests in `tests/test_perf.py` must enforce this budget.
* **Strictly Air-Gapped / Zero Network:** Zero network calls allowed anywhere in the runtime. No telemetry, no web endpoints.
* **Zero Heavy Clipboard Dependencies:** Clipboard integration must use lightweight platform binaries (`pbcopy`, `wl-copy`, `xclip`, `xsel`) rather than heavy multi-dependency packages.

## 5. Agentic Context Management (Headroom MCP)
If the Headroom MCP server (`mcp__headroom__*`) is available:
1. **Context Compression:** Before ingesting large tool outputs (test logs, benchmarks, diffs > 100 lines), route text through `mcp__headroom__headroom_compress`.
2. **Detail Retrieval (CCR):** Use `mcp__headroom__headroom_retrieve` on demand for specific code chunks or error traces.
