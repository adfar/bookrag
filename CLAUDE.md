# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bookrag is a Python CLI tool that converts markdown manuscripts into single-file interactive web books with optional AI chat integration. The tool is designed primarily for educational content (textbooks, course materials).

## Development Setup

This project uses `uv` for package management. The main implementation is in the `.worktrees/implement-bookrag/` directory (git worktree).

```bash
# Work in the worktree directory
cd .worktrees/implement-bookrag

# Install dependencies (uv handles venv automatically)
uv sync

# Install in editable mode
uv pip install -e .
```

**External dependency:** Pandoc must be installed on the system (`brew install pandoc` on macOS, `apt-get install pandoc` on Ubuntu).

## Common Commands

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run single test
pytest tests/test_config.py::test_load_valid_config -v
```

### Building a Book
```bash
# Basic usage
bookrag build <source-dir> <output-file>

# Example with test fixtures
bookrag build tests/fixtures/sample-book output.html
```

### Linting
Currently no linting configured. Consider adding ruff or black if needed.

## Architecture

### Build Pipeline Flow
1. **Config Loading** (`config.py`): Parse and validate `bookrag.yaml`
2. **Chapter Processing** (`builder.py`): For each chapter:
   - Read `content.md` from chapter folder
   - Convert markdown → HTML via Pandoc subprocess
   - Wrap in `<div class="chapter" id="chapter-{id}">` with show/hide logic
3. **TOC Generation** (`builder.py`): Generate navigation list from config
4. **Template Rendering** (`builder.py`): Use Jinja2 to assemble final HTML
   - Inject TOC, chapters, optional chat widget
   - Embed book content as JSON for AI context
   - Apply layout class (`two-column` or `three-column`)
5. **Output**: Single self-contained HTML file

### Key Components

**CLI (`cli.py`)**: Click-based command interface. Single `build` command that delegates to `build_book()`.

**Config (`config.py`)**: YAML parsing with validation. Required fields: `title`, `chapters` (each with `id`, `title`, `folder`). Optional: `ai` block with `backend`, `model`, `api_key_env`, `system_prompt`.

**Builder (`builder.py`)**:
- `build_book()`: Main orchestrator function
- `convert_markdown_to_html()`: Pandoc subprocess wrapper
- `generate_toc()`: Creates HTML list items from chapter metadata

**Templates (`templates/book.html`)**: Jinja2 template with:
- Responsive grid layout (CSS Grid)
- Minimal vanilla CSS (no framework)
- JavaScript for chapter navigation (show/hide divs)
- Optional chat widget with AI backend integration

### Layout Architecture
The tool generates either **2-column** (TOC + Content) or **3-column** (TOC + Content + Chat) layouts:
- All chapters are embedded in the HTML but hidden with `display:none`
- JavaScript handles show/hide on TOC link clicks (SPA-style navigation)
- If AI is configured, the full book markdown is embedded as a JS variable for context

### AI Integration
When AI is configured:
- Chat widget appears in right column
- Book content is embedded in `<script>` as JSON
- JavaScript handles API calls to Anthropic/OpenAI/Ollama
- System prompt includes full book text for context-aware responses
- API keys read from environment variables (not embedded)

## Testing Structure

Tests use pytest with fixtures in `tests/fixtures/`:
- `valid-config.yaml` / `minimal-config.yaml` / `invalid-config.yaml`: Config test cases
- `sample-book/`: Full test book with chapters for integration tests

**Test Organization:**
- `test_config.py`: Config loading and validation
- `test_builder.py`: Chapter processing, TOC generation, pandoc integration
- `test_cli.py`: CLI argument handling
- `test_integration.py`: End-to-end build process

## Project Structure Conventions

**User's book project structure:**
```
my-book/
├── bookrag.yaml           # Config file
├── 01-intro/
│   └── content.md         # Chapter markdown
├── 02-chapter1/
│   └── content.md
└── output.html           # Generated output (not tracked)
```

**Python package structure:**
```
bookrag/
├── __init__.py           # Version string
├── cli.py                # Click commands
├── config.py             # YAML parsing
├── builder.py            # Build orchestration
└── templates/
    └── book.html         # Jinja2 template
```

## Important Notes

- The worktree at `.worktrees/implement-bookrag/` is where active development happens
- Main repo root is mostly docs and git metadata
- Pandoc is a critical external dependency - the tool will fail gracefully if missing
- Output HTML files are completely self-contained (no external dependencies at runtime)
- API keys are never embedded in HTML - they're requested from user or read from env vars in browser
