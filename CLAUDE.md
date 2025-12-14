# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bookrag is a Python CLI tool that converts markdown manuscripts into interactive web books with RAG-based AI chat. It uses local Ollama models for both embeddings and chat, making it fully offline-capable.

## Development Setup

This project uses `uv` for package management.

```bash
# Install dependencies
uv sync

# Install in editable mode
uv pip install -e .
```

**External dependencies:**
- Pandoc: `brew install pandoc` (macOS) or `apt-get install pandoc` (Ubuntu)
- Ollama: `brew install ollama` (macOS) or see https://ollama.ai/

**Required Ollama models:**
```bash
ollama pull llama3.2          # Chat model
ollama pull nomic-embed-text  # Embedding model
```

## Common Commands

### Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_chunker.py -v
```

### Building a Book
```bash
# Ensure Ollama is running first
ollama serve

# Build book
bookrag build <source-dir> <output-file>

# Example
bookrag build tests/fixtures/sample-book output.html
```

## Architecture

### Build Pipeline Flow
1. **Config Loading** (`config.py`): Parse and validate `bookrag.yaml`
2. **Ollama Check**: Verify Ollama is running
3. **Chapter Processing** (`builder.py`): For each chapter:
   - Read `content.md` from chapter folder
   - Chunk content by headings (max 500 tokens)
   - Convert markdown → HTML via Pandoc
4. **Embedding Generation** (`embeddings.py`): Generate embeddings for all chunks via Ollama
5. **Template Rendering** (`builder.py`): Assemble final HTML with chunks embedded
6. **Output**: `output.html` + `chunks.json`

### Key Components

**CLI (`cli.py`)**: Click-based command interface. Single `build` command.

**Config (`config.py`)**: YAML parsing with validation. Required fields:
- `title`, `model`, `embedding_model`, `system_prompt`
- `chapters` (each with `id`, `title`, `folder`)

**Chunker (`chunker.py`)**:
- `chunk_markdown()`: Split content by headings, then paragraphs if too long
- `Chunk` dataclass with id, chapter_id, heading, content, token_count

**Embeddings (`embeddings.py`)**:
- `generate_embeddings()`: Call Ollama `/api/embeddings` for each chunk
- `ChunkWithEmbedding` dataclass extends Chunk with embedding vector
- `check_ollama_available()`: Verify Ollama is running

**Builder (`builder.py`)**:
- `build_book()`: Main orchestrator function
- Chunks content, generates embeddings, renders template

**Templates (`templates/book.html`)**: Jinja2 template with:
- 3-column grid layout (TOC, Content, Chat)
- JavaScript RAG implementation:
  - `cosineSimilarity()`: Vector comparison
  - `getQueryEmbedding()`: Call Ollama embeddings API
  - `findRelevantChunks()`: Semantic search
  - `sendToOllama()`: RAG-enhanced chat

### RAG Flow (Runtime)
1. User sends message
2. Browser calls Ollama `/api/embeddings` to embed query
3. Cosine similarity against pre-computed chunk embeddings
4. Top-3 chunks retrieved
5. System prompt + retrieved context + user message → Ollama chat
6. Response displayed

## Testing Structure

Tests use pytest with fixtures in `tests/fixtures/`:
- `valid-config.yaml` / `minimal-config.yaml`: Config test cases
- `sample-book/`: Full test book with chapters

**Test Organization:**
- `test_config.py`: Config loading and validation
- `test_chunker.py`: Chunking logic
- `test_embeddings.py`: Embedding generation (mocked)
- `test_builder.py`: TOC generation
- `test_cli.py`: CLI argument handling
- `test_integration.py`: End-to-end build (mocked Ollama)

## Project Structure

**User's book project:**
```
my-book/
├── bookrag.yaml           # Config file
├── 01-intro/
│   └── content.md         # Chapter markdown
├── output.html            # Generated book
└── chunks.json            # Embeddings for RAG
```

**Python package:**
```
bookrag/
├── __init__.py            # Version string
├── cli.py                 # Click commands
├── config.py              # YAML parsing
├── chunker.py             # Content chunking
├── embeddings.py          # Ollama embeddings
├── builder.py             # Build orchestration
└── templates/
    └── book.html          # Jinja2 template with RAG JS
```

## Important Notes

- Ollama must be running for both build (embeddings) and runtime (chat)
- All AI processing happens locally via Ollama - no external API keys needed
- Chunks are embedded at build time, stored in output for fast runtime retrieval
- Tests mock Ollama to run without it installed
