# Configuration Guide

## Config File Format

The `bookrag.yaml` file controls all aspects of your book build.

## Required Fields

### `title`
Book title displayed in TOC and page title.

```yaml
title: "Introduction to Python"
```

### `chapters`
List of chapters in order. Each chapter requires:
- `id`: Unique identifier (used in URLs and HTML IDs)
- `title`: Display title in TOC
- `folder`: Folder name containing `content.md`

```yaml
chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
  - id: "basics"
    title: "Python Basics"
    folder: "02-basics"
```

## Optional Fields

### `author`
Author name (metadata only, not currently displayed).

```yaml
author: "Jane Doe"
```

### `ai`
AI chat configuration. If omitted, book is generated without chat widget.

```yaml
ai:
  backend: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"
  system_prompt: "You are a helpful Python tutor."
```

#### AI Backend Options

**Anthropic Claude:**
```yaml
ai:
  backend: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"
  system_prompt: "Your system prompt here"
```

**OpenAI GPT:**
```yaml
ai:
  backend: "openai"
  model: "gpt-4"
  api_key_env: "OPENAI_API_KEY"
  system_prompt: "Your system prompt here"
```

**Ollama (Local):**
```yaml
ai:
  backend: "ollama"
  model: "llama2"
  base_url: "http://localhost:11434"  # Optional, defaults to localhost
  system_prompt: "Your system prompt here"
```

## Complete Example

```yaml
title: "Machine Learning Fundamentals"
author: "Dr. Jane Smith"

ai:
  backend: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"
  system_prompt: |
    You are an expert machine learning tutor. Help students understand
    concepts from this textbook. Provide clear explanations and examples.

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
  - id: "linear-regression"
    title: "Linear Regression"
    folder: "02-linear-regression"
  - id: "neural-networks"
    title: "Neural Networks"
    folder: "03-neural-networks"
  - id: "deep-learning"
    title: "Deep Learning"
    folder: "04-deep-learning"
```

## Validation

Bookrag validates your config and provides clear error messages:

- Missing required fields
- Invalid chapter structure
- Unsupported AI backend
- Missing chapter folders

Run `bookrag build` to validate your configuration.
