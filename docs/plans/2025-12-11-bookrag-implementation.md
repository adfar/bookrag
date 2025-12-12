# Bookrag Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that converts markdown manuscripts into interactive web books with optional AI chat.

**Architecture:** Hybrid approach using pandoc for markdown→HTML conversion with Python orchestrating the build process. Single-page HTML with all chapters loaded, JavaScript show/hide for navigation. Optional 3-column layout (TOC, content, chat) or 2-column (TOC, content only).

**Tech Stack:** Python 3.8+, Click (CLI), PyYAML (config), Jinja2 (templating), Pandoc (markdown conversion), vanilla JavaScript (no frameworks).

---

## Task 1: Project Structure Setup

**Files:**
- Create: `setup.py`
- Create: `bookrag/__init__.py`
- Create: `bookrag/cli.py`
- Create: `bookrag/builder.py`
- Create: `bookrag/config.py`
- Create: `README.md`

**Step 1: Write setup.py**

```python
from setuptools import setup, find_packages

setup(
    name="bookrag",
    version="0.1.0",
    description="Convert markdown manuscripts into interactive web books with AI chat",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "PyYAML>=6.0",
        "Jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bookrag=bookrag.cli:cli",
        ],
    },
    python_requires=">=3.8",
)
```

**Step 2: Create package __init__.py**

```python
"""Bookrag - Convert markdown manuscripts into interactive web books."""

__version__ = "0.1.0"
```

**Step 3: Create empty module files**

```python
# bookrag/cli.py
"""Command-line interface for bookrag."""
pass

# bookrag/builder.py
"""Main build logic for converting markdown to web book."""
pass

# bookrag/config.py
"""Configuration file parsing and validation."""
pass
```

**Step 4: Write basic README**

```markdown
# Bookrag

Convert markdown manuscripts into interactive web books with optional AI chat.

## Installation

```bash
pip install -e .
```

## Usage

```bash
bookrag build <source-dir> <output-file>
```

## Configuration

Create a `bookrag.yaml` in your source directory. See documentation for details.
```

**Step 5: Install in development mode**

Run: `pip install -e .`
Expected: Package installs successfully

**Step 6: Commit**

```bash
git add setup.py bookrag/ README.md
git commit -m "feat: initial project structure"
```

---

## Task 2: Config Module (TDD)

**Files:**
- Create: `tests/test_config.py`
- Modify: `bookrag/config.py`
- Create: `tests/fixtures/valid-config.yaml`
- Create: `tests/fixtures/minimal-config.yaml`

**Step 1: Write failing test for basic config loading**

Create `tests/test_config.py`:

```python
import pytest
from pathlib import Path
from bookrag.config import load_config

def test_load_valid_config():
    """Test loading a valid config file."""
    config_path = Path(__file__).parent / "fixtures" / "valid-config.yaml"
    config = load_config(config_path)

    assert config["title"] == "Test Book"
    assert config["author"] == "Test Author"
    assert len(config["chapters"]) == 2
    assert config["chapters"][0]["id"] == "intro"
    assert config["chapters"][0]["title"] == "Introduction"
    assert config["chapters"][0]["folder"] == "01-intro"

def test_load_minimal_config():
    """Test loading config without optional AI settings."""
    config_path = Path(__file__).parent / "fixtures" / "minimal-config.yaml"
    config = load_config(config_path)

    assert config["title"] == "Minimal Book"
    assert "ai" not in config
    assert len(config["chapters"]) == 1

def test_missing_required_fields():
    """Test that missing title raises error."""
    with pytest.raises(ValueError, match="Missing required field: title"):
        load_config(Path("nonexistent.yaml"))
```

**Step 2: Create test fixtures**

Create `tests/fixtures/valid-config.yaml`:

```yaml
title: "Test Book"
author: "Test Author"

ai:
  backend: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"
  system_prompt: "You are a helpful tutor."

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-intro"
  - id: "chapter1"
    title: "Chapter 1"
    folder: "02-chapter1"
```

Create `tests/fixtures/minimal-config.yaml`:

```yaml
title: "Minimal Book"
author: "Test Author"

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-intro"
```

**Step 3: Run tests to verify they fail**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError" or "ImportError"

**Step 4: Implement config loading**

Update `bookrag/config.py`:

```python
"""Configuration file parsing and validation."""
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate configuration file.

    Args:
        config_path: Path to bookrag.yaml config file

    Returns:
        Validated config dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required fields are missing or invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if not config.get("title"):
        raise ValueError("Missing required field: title")

    if not config.get("chapters"):
        raise ValueError("Missing required field: chapters")

    # Validate chapters structure
    for i, chapter in enumerate(config["chapters"]):
        if not chapter.get("id"):
            raise ValueError(f"Chapter {i}: missing required field 'id'")
        if not chapter.get("title"):
            raise ValueError(f"Chapter {i}: missing required field 'title'")
        if not chapter.get("folder"):
            raise ValueError(f"Chapter {i}: missing required field 'folder'")

    # Validate AI config if present
    if "ai" in config:
        ai = config["ai"]
        if not ai.get("backend"):
            raise ValueError("AI config missing required field: backend")

        supported_backends = ["anthropic", "openai", "ollama"]
        if ai["backend"] not in supported_backends:
            raise ValueError(
                f"Unsupported AI backend: {ai['backend']}. "
                f"Supported: {', '.join(supported_backends)}"
            )

    return config
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: PASS (all 3 tests)

**Step 6: Commit**

```bash
git add tests/test_config.py tests/fixtures/ bookrag/config.py
git commit -m "feat: add config loading and validation with tests"
```

---

## Task 3: CLI Module (TDD)

**Files:**
- Create: `tests/test_cli.py`
- Modify: `bookrag/cli.py`

**Step 1: Write failing test for CLI**

Create `tests/test_cli.py`:

```python
from click.testing import CliRunner
from bookrag.cli import cli

def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert 'bookrag' in result.output.lower()
    assert 'build' in result.output.lower()

def test_build_command_requires_args():
    """Test that build command requires source and output args."""
    runner = CliRunner()
    result = runner.invoke(cli, ['build'])

    assert result.exit_code != 0
    assert 'Missing argument' in result.output or 'Usage:' in result.output
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL with import or attribute errors

**Step 3: Implement CLI**

Update `bookrag/cli.py`:

```python
"""Command-line interface for bookrag."""
import click
from pathlib import Path
from bookrag.builder import build_book

@click.group()
@click.version_option()
def cli():
    """Bookrag - Convert markdown manuscripts into interactive web books."""
    pass

@cli.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
def build(source_dir: Path, output_file: Path):
    """Build a web book from markdown source.

    SOURCE_DIR: Directory containing bookrag.yaml and chapter folders
    OUTPUT_FILE: Path for the generated HTML file
    """
    try:
        build_book(source_dir, output_file)
        click.echo(f"✓ Book built successfully: {output_file}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add tests/test_cli.py bookrag/cli.py
git commit -m "feat: add CLI with build command"
```

---

## Task 4: Pandoc Template (HTML Structure)

**Files:**
- Create: `bookrag/templates/book.html`

**Step 1: Create pandoc HTML template**

Create `bookrag/templates/book.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }

        .book-container {
            display: grid;
            height: 100vh;
            overflow: hidden;
        }

        .book-container.two-column {
            grid-template-columns: 250px 1fr;
        }

        .book-container.three-column {
            grid-template-columns: 250px 1fr 350px;
        }

        /* Table of Contents */
        .toc {
            background: #f8f9fa;
            border-right: 1px solid #dee2e6;
            padding: 20px;
            overflow-y: auto;
        }

        .toc h2 {
            font-size: 18px;
            margin-bottom: 20px;
            color: #212529;
        }

        .toc ul {
            list-style: none;
        }

        .toc li {
            margin-bottom: 8px;
        }

        .toc a {
            color: #495057;
            text-decoration: none;
            display: block;
            padding: 8px 12px;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .toc a:hover {
            background: #e9ecef;
            color: #212529;
        }

        .toc a.active {
            background: #007bff;
            color: white;
        }

        /* Content Area */
        .content {
            padding: 40px 60px;
            overflow-y: auto;
        }

        .chapter {
            display: none;
            max-width: 800px;
            margin: 0 auto;
        }

        .chapter.active {
            display: block;
        }

        .content h1 {
            font-size: 32px;
            margin-bottom: 24px;
            color: #212529;
        }

        .content h2 {
            font-size: 24px;
            margin-top: 32px;
            margin-bottom: 16px;
            color: #343a40;
        }

        .content h3 {
            font-size: 20px;
            margin-top: 24px;
            margin-bottom: 12px;
            color: #495057;
        }

        .content p {
            margin-bottom: 16px;
        }

        .content pre {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 16px;
            overflow-x: auto;
            margin-bottom: 16px;
        }

        .content code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 14px;
        }

        .content pre code {
            background: none;
            padding: 0;
        }

        .content ul, .content ol {
            margin-bottom: 16px;
            padding-left: 32px;
        }

        .content li {
            margin-bottom: 8px;
        }

        /* Chat Widget */
        .chat-widget {
            display: flex;
            flex-direction: column;
            background: #fff;
            border-left: 1px solid #dee2e6;
        }

        .chat-header {
            background: #007bff;
            color: white;
            padding: 16px 20px;
            font-weight: 600;
            font-size: 16px;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }

        .chat-message {
            margin-bottom: 16px;
        }

        .chat-message.user {
            text-align: right;
        }

        .chat-message.assistant {
            text-align: left;
        }

        .chat-message .bubble {
            display: inline-block;
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            word-wrap: break-word;
        }

        .chat-message.user .bubble {
            background: #007bff;
            color: white;
        }

        .chat-message.assistant .bubble {
            background: #f8f9fa;
            color: #212529;
        }

        .chat-input {
            border-top: 1px solid #dee2e6;
            padding: 16px;
        }

        .chat-input textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            resize: vertical;
            min-height: 60px;
            font-family: inherit;
            font-size: 14px;
        }

        .chat-input button {
            width: 100%;
            margin-top: 8px;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }

        .chat-input button:hover {
            background: #0056b3;
        }

        .chat-input button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 12px;
        }
    </style>
</head>
<body>
    <div class="book-container {{ layout_class }}">
        <!-- Table of Contents -->
        <nav class="toc">
            <h2>{{ title }}</h2>
            <ul id="toc-list">
                {{ toc_html|safe }}
            </ul>
        </nav>

        <!-- Content Area -->
        <main class="content">
            {{ chapters_html|safe }}
        </main>

        <!-- Chat Widget (only if AI configured) -->
        {% if chat_html %}
        {{ chat_html|safe }}
        {% endif %}
    </div>

    <script>
        // Book content for AI context
        const BOOK_CONTENT = {{ book_content_json|safe }};

        // Chat configuration
        const CHAT_CONFIG = {{ chat_config_json|safe }};

        // Chapter navigation
        document.addEventListener('DOMContentLoaded', function() {
            const tocLinks = document.querySelectorAll('#toc-list a');
            const chapters = document.querySelectorAll('.chapter');

            tocLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const chapterId = this.dataset.chapterId;

                    // Update active TOC link
                    tocLinks.forEach(l => l.classList.remove('active'));
                    this.classList.add('active');

                    // Show selected chapter
                    chapters.forEach(ch => ch.classList.remove('active'));
                    document.getElementById(`chapter-${chapterId}`).classList.add('active');
                });
            });

            // Activate first chapter by default
            if (tocLinks.length > 0) {
                tocLinks[0].classList.add('active');
            }
            if (chapters.length > 0) {
                chapters[0].classList.add('active');
            }

            // Initialize chat if configured
            if (CHAT_CONFIG) {
                initializeChat();
            }
        });

        // Chat functionality
        function initializeChat() {
            const sendBtn = document.getElementById('send-btn');
            const userInput = document.getElementById('user-input');
            const messagesContainer = document.getElementById('chat-messages');

            if (!sendBtn || !userInput || !messagesContainer) return;

            sendBtn.addEventListener('click', handleSend);
            userInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                }
            });

            async function handleSend() {
                const message = userInput.value.trim();
                if (!message) return;

                // Add user message to UI
                addMessage('user', message);
                userInput.value = '';
                sendBtn.disabled = true;

                try {
                    // Send to AI
                    const response = await sendToAI(message);
                    addMessage('assistant', response);
                } catch (error) {
                    showError(error.message);
                } finally {
                    sendBtn.disabled = false;
                }
            }

            function addMessage(role, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `chat-message ${role}`;

                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.textContent = content;

                messageDiv.appendChild(bubble);
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = `Error: ${message}`;
                messagesContainer.appendChild(errorDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            async function sendToAI(userMessage) {
                const backend = CHAT_CONFIG.backend;

                // Build system prompt with book content
                const systemPrompt = CHAT_CONFIG.system_prompt +
                    "\\n\\nBook content:\\n" + BOOK_CONTENT;

                if (backend === 'anthropic') {
                    return await callAnthropic(systemPrompt, userMessage);
                } else if (backend === 'openai') {
                    return await callOpenAI(systemPrompt, userMessage);
                } else if (backend === 'ollama') {
                    return await callOllama(systemPrompt, userMessage);
                } else {
                    throw new Error(`Unsupported backend: ${backend}`);
                }
            }

            async function callAnthropic(systemPrompt, userMessage) {
                const apiKey = prompt('Enter your Anthropic API key:');
                if (!apiKey) throw new Error('API key required');

                const response = await fetch('https://api.anthropic.com/v1/messages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-api-key': apiKey,
                        'anthropic-version': '2023-06-01'
                    },
                    body: JSON.stringify({
                        model: CHAT_CONFIG.model || 'claude-3-5-sonnet-20241022',
                        max_tokens: 1024,
                        system: systemPrompt,
                        messages: [
                            { role: 'user', content: userMessage }
                        ]
                    })
                });

                if (!response.ok) {
                    throw new Error(`API request failed: ${response.statusText}`);
                }

                const data = await response.json();
                return data.content[0].text;
            }

            async function callOpenAI(systemPrompt, userMessage) {
                const apiKey = prompt('Enter your OpenAI API key:');
                if (!apiKey) throw new Error('API key required');

                const response = await fetch('https://api.openai.com/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${apiKey}`
                    },
                    body: JSON.stringify({
                        model: CHAT_CONFIG.model || 'gpt-4',
                        messages: [
                            { role: 'system', content: systemPrompt },
                            { role: 'user', content: userMessage }
                        ]
                    })
                });

                if (!response.ok) {
                    throw new Error(`API request failed: ${response.statusText}`);
                }

                const data = await response.json();
                return data.choices[0].message.content;
            }

            async function callOllama(systemPrompt, userMessage) {
                const baseUrl = CHAT_CONFIG.base_url || 'http://localhost:11434';

                const response = await fetch(`${baseUrl}/api/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        model: CHAT_CONFIG.model || 'llama2',
                        messages: [
                            { role: 'system', content: systemPrompt },
                            { role: 'user', content: userMessage }
                        ],
                        stream: false
                    })
                });

                if (!response.ok) {
                    throw new Error(`API request failed: ${response.statusText}`);
                }

                const data = await response.json();
                return data.message.content;
            }
        }
    </script>
</body>
</html>
```

**Step 2: Commit**

```bash
git add bookrag/templates/book.html
git commit -m "feat: add HTML template with CSS and JavaScript"
```

---

## Task 5: Builder Module - Core Logic (TDD)

**Files:**
- Create: `tests/test_builder.py`
- Modify: `bookrag/builder.py`
- Create: `tests/fixtures/sample-book/`

**Step 1: Create sample book fixture**

Create directory structure:
```bash
mkdir -p tests/fixtures/sample-book/01-intro
mkdir -p tests/fixtures/sample-book/02-chapter1
```

Create `tests/fixtures/sample-book/bookrag.yaml`:
```yaml
title: "Sample Book"
author: "Test Author"

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-intro"
  - id: "chapter1"
    title: "Chapter 1"
    folder: "02-chapter1"
```

Create `tests/fixtures/sample-book/01-intro/content.md`:
```markdown
# Introduction

This is the introduction chapter.

## Overview

Welcome to the book!
```

Create `tests/fixtures/sample-book/02-chapter1/content.md`:
```markdown
# Chapter 1: Getting Started

This is the first chapter.

## Section 1.1

Some content here.
```

**Step 2: Write failing test for TOC generation**

Create `tests/test_builder.py`:

```python
import pytest
from pathlib import Path
from bookrag.builder import generate_toc

def test_generate_toc():
    """Test TOC HTML generation from chapters config."""
    chapters = [
        {"id": "intro", "title": "Introduction"},
        {"id": "chapter1", "title": "Chapter 1"},
    ]

    toc_html = generate_toc(chapters)

    assert '<li>' in toc_html
    assert 'data-chapter-id="intro"' in toc_html
    assert 'Introduction' in toc_html
    assert 'data-chapter-id="chapter1"' in toc_html
    assert 'Chapter 1' in toc_html
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_builder.py::test_generate_toc -v`
Expected: FAIL with ImportError or AttributeError

**Step 4: Implement generate_toc**

Update `bookrag/builder.py`:

```python
"""Main build logic for converting markdown to web book."""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bookrag.config import load_config

def generate_toc(chapters: List[Dict[str, str]]) -> str:
    """Generate TOC HTML from chapters list.

    Args:
        chapters: List of chapter dicts with id and title

    Returns:
        HTML string for TOC list items
    """
    toc_items = []
    for chapter in chapters:
        toc_items.append(
            f'<li><a href="#" data-chapter-id="{chapter["id"]}">{chapter["title"]}</a></li>'
        )
    return '\n'.join(toc_items)


def build_book(source_dir: Path, output_file: Path):
    """Build web book from markdown source.

    Args:
        source_dir: Directory containing bookrag.yaml and chapters
        output_file: Path for output HTML file

    Raises:
        FileNotFoundError: If config or chapter files missing
        subprocess.CalledProcessError: If pandoc fails
    """
    # Load and validate config
    config_path = source_dir / "bookrag.yaml"
    config = load_config(config_path)

    # Check if AI is configured
    has_ai = "ai" in config
    layout_class = "three-column" if has_ai else "two-column"

    # Process each chapter through pandoc
    chapters_html = []
    book_content_parts = []

    for i, chapter in enumerate(config["chapters"]):
        chapter_folder = source_dir / chapter["folder"]
        chapter_file = chapter_folder / "content.md"

        if not chapter_file.exists():
            raise FileNotFoundError(f"Chapter file not found: {chapter_file}")

        # Read markdown for book content
        with open(chapter_file, 'r') as f:
            book_content_parts.append(f.read())

        # Convert with pandoc
        chapter_html = convert_markdown_to_html(chapter_file)

        # Wrap in chapter div
        display = "block" if i == 0 else "none"
        wrapped_html = (
            f'<div class="chapter" id="chapter-{chapter["id"]}" '
            f'style="display:{display}">\n{chapter_html}\n</div>'
        )
        chapters_html.append(wrapped_html)

    # Generate TOC
    toc_html = generate_toc(config["chapters"])

    # Prepare chat widget HTML if AI configured
    chat_html = ""
    if has_ai:
        chat_html = '''
        <aside class="chat-widget">
            <div class="chat-header">AI Assistant</div>
            <div class="chat-messages" id="chat-messages"></div>
            <div class="chat-input">
                <textarea id="user-input" placeholder="Ask a question..."></textarea>
                <button id="send-btn">Send</button>
            </div>
        </aside>
        '''

    # Prepare template variables
    template_vars = {
        "title": config.get("title", "Book"),
        "author": config.get("author", ""),
        "layout_class": layout_class,
        "toc_html": toc_html,
        "chapters_html": "\n".join(chapters_html),
        "chat_html": chat_html,
        "book_content_json": json.dumps("\n\n".join(book_content_parts)),
        "chat_config_json": json.dumps(config.get("ai")) if has_ai else "null",
    }

    # Render template
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("book.html")
    output_html = template.render(**template_vars)

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(output_html)


def convert_markdown_to_html(markdown_file: Path) -> str:
    """Convert markdown file to HTML using pandoc.

    Args:
        markdown_file: Path to markdown file

    Returns:
        HTML string (body content only, not standalone)

    Raises:
        subprocess.CalledProcessError: If pandoc fails
        FileNotFoundError: If pandoc not installed
    """
    try:
        result = subprocess.run(
            ["pandoc", str(markdown_file), "-f", "markdown", "-t", "html"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except FileNotFoundError:
        raise FileNotFoundError(
            "Pandoc not found. Please install pandoc: https://pandoc.org/installing.html"
        )
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_builder.py::test_generate_toc -v`
Expected: PASS

**Step 6: Commit**

```bash
git add tests/test_builder.py tests/fixtures/sample-book/ bookrag/builder.py
git commit -m "feat: add TOC generation and core builder logic"
```

---

## Task 6: Integration Test - End to End

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
import pytest
from pathlib import Path
from bookrag.builder import build_book

def test_build_sample_book(tmp_path):
    """Test building complete book from sample fixture."""
    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    build_book(source_dir, output_file)

    # Verify output exists
    assert output_file.exists()

    # Verify HTML content
    html_content = output_file.read_text()
    assert '<title>Sample Book</title>' in html_content
    assert 'Introduction' in html_content
    assert 'Chapter 1' in html_content
    assert 'This is the introduction chapter' in html_content
    assert 'class="book-container two-column"' in html_content  # No AI
    assert 'chapter-intro' in html_content
    assert 'chapter-chapter1' in html_content

def test_build_with_ai_config(tmp_path):
    """Test building book with AI chat enabled."""
    # Create test book with AI config
    source_dir = tmp_path / "book-with-ai"
    source_dir.mkdir()

    config_content = """
title: "AI-Enabled Book"
author: "Test"

ai:
  backend: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  system_prompt: "You are a helpful tutor."

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-intro"
"""
    (source_dir / "bookrag.yaml").write_text(config_content)

    chapter_dir = source_dir / "01-intro"
    chapter_dir.mkdir()
    (chapter_dir / "content.md").write_text("# Intro\n\nTest content.")

    output_file = tmp_path / "output-ai.html"
    build_book(source_dir, output_file)

    html_content = output_file.read_text()
    assert 'three-column' in html_content
    assert 'chat-widget' in html_content
    assert 'AI Assistant' in html_content

def test_pandoc_not_installed(tmp_path, monkeypatch):
    """Test graceful error when pandoc not installed."""
    import subprocess

    def mock_run(*args, **kwargs):
        raise FileNotFoundError("pandoc not found")

    monkeypatch.setattr(subprocess, "run", mock_run)

    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    with pytest.raises(FileNotFoundError, match="Pandoc not found"):
        build_book(source_dir, output_file)
```

**Step 2: Run integration tests**

Run: `pytest tests/test_integration.py -v`
Expected: PASS (all 3 tests)

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration tests"
```

---

## Task 7: CLI Integration Test

**Files:**
- Modify: `tests/test_cli.py`

**Step 1: Add CLI integration test**

Add to `tests/test_cli.py`:

```python
def test_build_command_success(tmp_path):
    """Test successful build via CLI."""
    from pathlib import Path

    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    runner = CliRunner()
    result = runner.invoke(cli, ['build', str(source_dir), str(output_file)])

    assert result.exit_code == 0
    assert 'successfully' in result.output.lower()
    assert output_file.exists()

def test_build_command_missing_config(tmp_path):
    """Test error handling for missing config."""
    source_dir = tmp_path / "no-config"
    source_dir.mkdir()
    output_file = tmp_path / "output.html"

    runner = CliRunner()
    result = runner.invoke(cli, ['build', str(source_dir), str(output_file)])

    assert result.exit_code != 0
    assert 'Error' in result.output
```

**Step 2: Run CLI tests**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (all 4 tests)

**Step 3: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: add CLI integration tests"
```

---

## Task 8: Documentation

**Files:**
- Modify: `README.md`
- Create: `docs/configuration.md`
- Create: `docs/examples.md`

**Step 1: Update README with complete usage**

Update `README.md`:

```markdown
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
```

**Step 2: Create configuration documentation**

Create `docs/configuration.md`:

```markdown
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
```

**Step 3: Create examples documentation**

Create `docs/examples.md`:

```markdown
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
```

**Step 4: Run all tests to verify everything works**

Run: `pytest tests/ -v`
Expected: All tests pass

**Step 5: Commit**

```bash
git add README.md docs/configuration.md docs/examples.md
git commit -m "docs: add comprehensive documentation"
```

---

## Task 9: Final Verification

**Step 1: Build sample book manually**

```bash
cd tests/fixtures/sample-book
bookrag build . ../../../sample-output.html
```

Expected: Successful build message

**Step 2: Open in browser and verify**

```bash
# macOS
open sample-output.html

# Linux
xdg-open sample-output.html

# Windows
start sample-output.html
```

Verify:
- TOC appears on left
- Introduction shows first
- Clicking "Chapter 1" switches content
- No chat widget (no AI config)
- Responsive layout

**Step 3: Run full test suite**

Run: `pytest tests/ -v --cov=bookrag --cov-report=term-missing`
Expected: All tests pass, good coverage

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final verification complete"
```

**Step 5: Tag release**

```bash
git tag v0.1.0
```

---

## Summary

Total tasks: 9
Estimated time: 2-3 hours for experienced developer

Key principles applied:
- **TDD**: Tests before implementation
- **DRY**: Reusable functions, no duplication
- **YAGNI**: Only features specified in design
- **Frequent commits**: After each task/subtask

The implementation is complete and ready for use!
