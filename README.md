# Bookrag

Convert markdown manuscripts into interactive web books with optional AI chat integration.

## Features

- 📚 Convert markdown manuscripts to single-page web books
- 🎨 Clean 3-column layout: TOC, content, AI chat
- 🤖 Optional AI chat with multiple backend support (Anthropic, OpenAI, Ollama)
- 📱 Responsive design with minimal CSS
- ⚙️ Flexible configuration via YAML
- 📁 Folder-based chapter organization

## Installation

Requires Python 3.8+ and [Pandoc](https://pandoc.org/installing.html).

```bash
# Install pandoc first
# macOS: brew install pandoc
# Ubuntu: apt-get install pandoc
# Windows: https://pandoc.org/installing.html

# Install bookrag
pip install -e .
```

## Quick Start

1. **Create project structure:**

```bash
mkdir my-book
cd my-book
mkdir 01-introduction 02-chapter-1
```

2. **Create `bookrag.yaml`:**

```yaml
title: "My Book"
author: "Your Name"

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
  - id: "chapter1"
    title: "Chapter 1"
    folder: "02-chapter-1"
```

3. **Add markdown content:**

```bash
echo "# Introduction\n\nWelcome to my book!" > 01-introduction/content.md
echo "# Chapter 1\n\nFirst chapter content." > 02-chapter-1/content.md
```

4. **Build the book:**

```bash
bookrag build . output.html
```

5. **Open `output.html` in your browser!**

## Configuration

See [docs/configuration.md](docs/configuration.md) for detailed configuration options.

### Basic Configuration (No AI)

```yaml
title: "Book Title"
author: "Author Name"

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
```

### With AI Chat

```yaml
title: "Book Title"
author: "Author Name"

ai:
  backend: "anthropic"  # or "openai", "ollama"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"
  system_prompt: "You are a helpful tutor for this textbook."

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
```

## AI Backend Support

- **Anthropic Claude**: Set `backend: "anthropic"`, requires API key
- **OpenAI GPT**: Set `backend: "openai"`, requires API key
- **Ollama (local)**: Set `backend: "ollama"`, specify `base_url` if needed

API keys are requested in the browser when first using chat.

## Project Structure

```
my-book/
├── bookrag.yaml          # Configuration
├── 01-introduction/
│   └── content.md        # Chapter markdown
├── 02-chapter-1/
│   └── content.md
└── output.html          # Generated book
```

## Examples

See [docs/examples.md](docs/examples.md) for complete examples.

## Testing

```bash
pytest tests/ -v
```

## License

MIT
