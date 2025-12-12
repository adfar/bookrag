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

        # Wrap in chapter div (first chapter gets active class)
        active_class = " active" if i == 0 else ""
        wrapped_html = (
            f'<div class="chapter{active_class}" id="chapter-{chapter["id"]}">'
            f'\n{chapter_html}\n</div>'
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
