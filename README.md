# Bookrag

Convert markdown manuscripts into interactive web books with AI-powered RAG chat.

## Features

- Convert markdown manuscripts to single-page web books
- 3-column layout: TOC, content, AI chat
- RAG-based AI chat using local Ollama models
- Semantic search across book content
- Responsive design with minimal CSS
- Flexible configuration via YAML
- Folder-based chapter organization

## Requirements

- Python 3.11+
- [Pandoc](https://pandoc.org/installing.html) for markdown conversion
- [Ollama](https://ollama.ai/) for AI chat and embeddings

## Installation

```bash
# Install pandoc
# macOS: brew install pandoc
# Ubuntu: apt-get install pandoc

# Install Ollama (https://ollama.ai/)
# macOS: brew install ollama

# Pull required models
ollama pull llama3.2          # Chat model
ollama pull nomic-embed-text  # Embedding model

# Install bookrag
pip install -e .
```

## Quick Start

1. **Start Ollama:**

```bash
ollama serve
```

2. **Create project structure:**

```bash
mkdir my-book
cd my-book
mkdir 01-introduction 02-chapter-1
```

3. **Create `bookrag.yaml`:**

```yaml
title: "My Book"
author: "Your Name"
model: "llama3.2"
embedding_model: "nomic-embed-text"
system_prompt: "You are a helpful tutor for this book."

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
  - id: "chapter1"
    title: "Chapter 1"
    folder: "02-chapter-1"
```

4. **Add markdown content:**

```bash
echo "# Introduction\n\nWelcome to my book!" > 01-introduction/content.md
echo "# Chapter 1\n\nFirst chapter content." > 02-chapter-1/content.md
```

5. **Build the book:**

```bash
bookrag build . output.html
```

6. **Open `output.html` in your browser!**

Make sure Ollama is running when viewing the book to enable chat.

## Configuration

### Required Fields

```yaml
title: "Book Title"                    # Book title
model: "llama3.2"                      # Ollama chat model
embedding_model: "nomic-embed-text"    # Ollama embedding model
system_prompt: "You are helpful."      # AI system prompt

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
```

### Optional Fields

```yaml
author: "Author Name"                  # Optional author
```

## How It Works

### Build Time
1. Parse chapters from markdown files
2. Chunk content by headings (max 500 tokens per chunk)
3. Generate embeddings via Ollama for each chunk
4. Convert markdown to HTML via Pandoc
5. Output `index.html` + `chunks.json`

### Runtime (in browser)
1. User asks a question
2. Query is embedded via Ollama API
3. Cosine similarity finds top-3 relevant chunks
4. Retrieved chunks + question sent to Ollama chat
5. Response displayed in chat widget

## Project Structure

```
my-book/
├── bookrag.yaml          # Configuration
├── 01-introduction/
│   └── content.md        # Chapter markdown
├── 02-chapter-1/
│   └── content.md
├── output.html           # Generated book
└── chunks.json           # Embeddings for RAG
```

## Testing

```bash
pytest tests/ -v
```

## License

MIT
