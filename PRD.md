# Product Requirements Document (PRD)

## 1. Executive Summary
**Project Name:** `tree-tui`  
**Goal:** Provide an offline, cross-platform terminal user interface (TUI) and CLI tool for converting raw indented text outlines into clean ASCII/Unicode directory tree diagrams, eliminating dependency on web services.

## 2. Problem Statement
Developers and architects frequently generate directory diagrams for README files, technical specifications, and architectural documentation. Existing solutions require either sending directory layouts to third-party web apps or manually manipulating text. Standard Unix tools do not allow live drafting and visualization of arbitrary, hypothetical project architectures.

## 3. Target User & Persona
- **Primary Persona:** Software engineers, data scientists, and technical architects working across Linux and macOS environments.
- **Key Need:** Rapid, deterministic conversion of indented markdown lists or copied text outlines into standardized ASCII/Unicode tree hierarchies without leaving the terminal.

## 4. Scope & Core Requirements
### 4.1 CLI Execution
- **Piped Ingestion:** Read indented text directly from `STDIN` (`cat outline.txt | tree-tui -t`).
- **File Ingestion:** Read indented text outlines from a specified text file path (`tree-tui outline.txt`).

### 4.2 Interactive Terminal UI (TUI)
- **Live Two-Pane Editing:** Left pane accepts indented text input; right pane updates rendered tree diagram in real time on keystroke.
- **Indentation Handling:** Support arbitrary indentation sizes (2-space, 4-space, tabs, dash prefixes `-`, or bullet markers `*`).
- **Clipboard Export:** One-key action to write the rendered tree diagram to the system clipboard across macOS (`pbcopy`), Wayland (`wl-copy`), and X11 (`xclip`).
- **Template Reset:** Single keybinding to restore default structure template.

### 4.3 Structure Generation Command (Shell Command Export)
- **Unix/Linux Command Generation:** Translate the user's drafted tree structure into an equivalent terminal command (e.g., using `mkdir -p` and `touch`) to create the entire directory and file structure on disk.
- **CLI & TUI Integration:**
  - CLI flag to output the creation command script directly (`tree-tui --generate-command` / `-c`).
  - TUI shortcut/action to view or copy the shell command directly to the clipboard.

### 4.4 Out of Scope (Phase 1)
- Bi-directional tree synchronization (modifying the rendered ASCII diagram directly to regenerate the indented text).
- Direct automatic disk modifications by the tool itself (the tool generates/exports the recommended terminal command for the user to review and execute, rather than writing directly to disk).
- Scanning or walking actual directory trees on disk (the tool is purely an outline-to-diagram and outline-to-command transformer).

## 5. Non-Functional Requirements
- **Performance:** Re-parsing and re-rendering of text inputs under 1,000 lines must occur within < 16ms (60 FPS responsiveness).
- **Portability:** Zero runtime dependencies beyond standard Python / Textual libraries; distributable via `uv tool`, `pipx`, or PyInstaller binary.
- **Platform Support:** Linux (x86_64/aarch64) and macOS (Apple Silicon/Intel).

## 6. Success Metrics
- 100% test pass rate across unit test suite covering diverse indentation, empty lines, and edge-case hierarchies.
- 0 network calls executed during runtime (fully offline utility).
