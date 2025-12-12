# Examples

## Minimal Book (No AI)

### Project Structure
```
minimal-book/
├── bookrag.yaml
└── 01-intro/
    └── content.md
```

### bookrag.yaml
```yaml
title: "Minimal Book"
author: "Author"

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-intro"
```

### Build
```bash
bookrag build minimal-book output.html
```

## Educational Textbook with AI

### Project Structure
```
python-textbook/
├── bookrag.yaml
├── 01-introduction/
│   └── content.md
├── 02-basics/
│   └── content.md
└── 03-advanced/
    └── content.md
```

### bookrag.yaml
```yaml
title: "Python Programming"
author: "Jane Doe"

ai:
  backend: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  system_prompt: |
    You are a helpful Python programming tutor. Answer questions about
    the textbook content. Provide code examples and explanations.

chapters:
  - id: "intro"
    title: "Introduction to Python"
    folder: "01-introduction"
  - id: "basics"
    title: "Python Basics"
    folder: "02-basics"
  - id: "advanced"
    title: "Advanced Topics"
    folder: "03-advanced"
```

### Build
```bash
export ANTHROPIC_API_KEY="your-key-here"
bookrag build python-textbook python-textbook.html
```

## Using Ollama (Local AI)

### bookrag.yaml
```yaml
title: "Local AI Book"
author: "Author"

ai:
  backend: "ollama"
  model: "llama2"
  base_url: "http://localhost:11434"
  system_prompt: "You are a helpful tutor."

chapters:
  - id: "chapter1"
    title: "Chapter 1"
    folder: "01-chapter1"
```

Make sure Ollama is running:
```bash
ollama serve
ollama pull llama2
bookrag build . output.html
```
