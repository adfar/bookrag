# Web Book Interface Design

## Overview

A Python command-line tool that converts markdown manuscripts into interactive web books with optional AI chat integration. Primarily designed for educational content (textbooks, course materials, study guides).

## Key Features

- 3-column layout: Table of Contents, Chapter Content, AI Chat (optional)
- Single-page application with chapter show/hide navigation
- Manual TOC specification via config file
- Folder-based chapter organization
- Flexible AI backend support (Anthropic, OpenAI, Ollama, etc.)
- Minimal custom CSS (no framework dependencies)
- Optional AI chat - can generate books without API configuration

## Project Structure

### Source Directory Layout
```
source-dir/
├── bookrag.yaml          # Main config file
├── 01-introduction/
│   └── content.md
├── 02-getting-started/
│   └── content.md
├── 03-core-concepts/
│   └── content.md
└── ...
```

### Config File (bookrag.yaml)
```yaml
title: "Your Book Title"
author: "Author Name"

# Optional AI configuration
ai:
  backend: "anthropic"  # or "openai", "ollama", etc.
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"  # env var name
  system_prompt: "You are a helpful tutor for this textbook..."

chapters:
  - id: "intro"
    title: "Introduction"
    folder: "01-introduction"
  - id: "getting-started"
    title: "Getting Started"
    folder: "02-getting-started"
  - id: "core-concepts"
    title: "Core Concepts"
    folder: "03-core-concepts"
```

### Python Package Structure
```
bookrag/
├── bookrag/
│   ├── __init__.py
│   ├── cli.py           # CLI entry point
│   ├── builder.py       # Main build logic
│   ├── config.py        # Config parsing/validation
│   └── templates/
│       └── template.html
├── setup.py
└── README.md
```

## HTML Structure

### 3-Column Layout (with AI)
```html
<!DOCTYPE html>
<html>
<head>
  <title>{{book_title}}</title>
  <style>/* minimal CSS */</style>
</head>
<body>
  <div class="book-container three-column">
    <!-- Left: TOC -->
    <nav class="toc">
      <h2>{{book_title}}</h2>
      <ul id="toc-list">
        <!-- Generated from config -->
      </ul>
    </nav>

    <!-- Middle: Content -->
    <main class="content">
      <div class="chapter" id="chapter-intro" style="display:block">
        <!-- Pandoc-converted markdown -->
      </div>
      <div class="chapter" id="chapter-getting-started" style="display:none">
        <!-- Pandoc-converted markdown -->
      </div>
      <!-- More chapters... -->
    </main>

    <!-- Right: Chat (optional) -->
    <aside class="chat-widget">
      <div class="chat-header">AI Assistant</div>
      <div class="chat-messages" id="chat-messages"></div>
      <div class="chat-input">
        <textarea id="user-input" placeholder="Ask a question..."></textarea>
        <button id="send-btn">Send</button>
      </div>
    </aside>
  </div>
  <script>/* Navigation & chat logic */</script>
</body>
</html>
```

### CSS Layout
```css
.book-container.two-column {
  display: grid;
  grid-template-columns: 250px 1fr;  /* TOC + Content */
  height: 100vh;
}

.book-container.three-column {
  display: grid;
  grid-template-columns: 250px 1fr 300px;  /* TOC + Content + Chat */
  height: 100vh;
}
```

All chapters are loaded in HTML but hidden with `display:none`. JavaScript shows/hides chapters on TOC click.

## Build Process

### Hybrid Pandoc + Python Approach

1. **Python reads config** - Parses `bookrag.yaml` and validates structure
2. **Process each chapter:**
   - Read `content.md` from chapter folder
   - Call pandoc: `pandoc content.md -o chapter.html --standalone=false`
   - Wrap in `<div class="chapter" id="chapter-{id}" style="display:none">`
3. **Generate TOC HTML** from config chapters list
4. **Assemble final HTML:**
   - Load pandoc template
   - Inject TOC list items
   - Inject all chapter divs (first one with `display:block`)
   - If AI configured: inject chat config JSON and full book text
   - Apply appropriate layout class (`two-column` or `three-column`)
5. **Write output.html**

### CLI Interface
```bash
bookrag build <source-dir> <output-file>
```

Example:
```bash
bookrag build ./my-book ./output/book.html
```

## JavaScript Functionality

### Chapter Navigation
```javascript
// TOC click handler
document.querySelectorAll('#toc-list a').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const chapterId = e.target.dataset.chapterId;

    // Hide all chapters
    document.querySelectorAll('.chapter').forEach(ch => {
      ch.style.display = 'none';
    });

    // Show selected chapter
    document.getElementById(`chapter-${chapterId}`).style.display = 'block';
  });
});
```

### AI Chat Implementation (Optional)

The full book content is embedded as a JavaScript variable:
```javascript
const BOOK_CONTENT = `...full markdown text...`;
const chatConfig = {/*injected from config*/};

async function sendMessage(userMessage) {
  // Build prompt with book context
  const systemPrompt = chatConfig.system_prompt +
    "\n\nBook content:\n" + BOOK_CONTENT;

  // Call appropriate AI backend
  if (chatConfig.backend === 'anthropic') {
    return await callAnthropic(systemPrompt, userMessage);
  } else if (chatConfig.backend === 'openai') {
    return await callOpenAI(systemPrompt, userMessage);
  }
  // ... other backends
}
```

Each backend has a separate function that handles API-specific request formats. The chat maintains conversation history in memory.

**Note:** API keys are read from environment variables or user input (never embedded in HTML).

## Python Implementation Details

### CLI Entry Point (cli.py)
```python
import click
from .builder import build_book

@click.command()
@click.argument('source_dir', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def build(source_dir, output_file):
    """Build a web book from markdown source."""
    build_book(source_dir, output_file)

if __name__ == '__main__':
    build()
```

### Main Builder Logic (builder.py)
```python
def build_book(source_dir, output_file):
    # 1. Load and validate config
    config = load_config(source_dir / 'bookrag.yaml')
    has_ai = 'ai' in config

    # 2. Process each chapter through pandoc
    chapters_html = []
    for chapter in config['chapters']:
        chapter_html = process_chapter(source_dir, chapter)
        chapters_html.append(chapter_html)

    # 3. Generate TOC
    toc_html = generate_toc(config['chapters'])

    # 4. Determine layout
    layout_class = 'three-column' if has_ai else 'two-column'
    chat_html = render_chat_widget(config['ai']) if has_ai else ''

    # 5. Assemble final HTML from template
    output = render_template(config, toc_html, chapters_html,
                            layout_class, chat_html)

    # 6. Write output
    Path(output_file).write_text(output)
```

### Config Validation (config.py)
```python
def load_config(config_path):
    # Check file exists
    # Parse YAML
    # Validate required fields: title, chapters
    # Validate optional fields: ai settings
    # Check chapter folders exist
    # If AI configured: validate backend is supported
    # Return config dict or raise clear error
```

## Error Handling & Validation

### Build-time Checks
- Config file exists and is valid YAML
- Required fields present: `title`, `chapters`
- Each chapter folder exists and contains `content.md`
- Pandoc is installed and accessible
- Template file is present
- Output directory is writable
- If AI configured: backend is supported

### Runtime Considerations
- **API keys:** JavaScript checks if API key is available before sending
- **Rate limiting:** Simple debouncing on chat send button
- **Error display:** User-friendly errors in chat UI ("API key missing", "Request failed")
- **Book size:** Warn if book content exceeds AI context limits (e.g., 100k tokens)

### Error Messages
The tool should fail fast with clear, actionable error messages:
- "Chapter folder '02-getting-started' not found"
- "Missing required field 'title' in bookrag.yaml"
- "Pandoc not found. Please install pandoc."
- "Unsupported AI backend: 'gpt5'. Supported: anthropic, openai, ollama"

## Future Enhancement Ideas

- Syntax highlighting for code blocks (highlight.js)
- Search functionality within the book
- Bookmark/progress tracking (localStorage)
- Export chat conversations
- Dark mode toggle
- Multiple TOC levels (nested sections)
- Chapter-specific metadata (author, date, tags)

## Testing Approach

1. Create sample book with 2-3 chapters
2. Test build process end-to-end
3. Test with and without AI configuration
4. Manually test navigation in browser
5. Test chat with different AI backends
6. Test error conditions (missing files, invalid config)
