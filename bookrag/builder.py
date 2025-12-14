"""Main build logic for converting markdown to web book."""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bookrag.config import load_config
from bookrag.chunker import chunk_markdown
from bookrag.embeddings import generate_embeddings, check_ollama_available, OllamaConnectionError

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

    # Check Ollama availability
    if not check_ollama_available():
        raise OllamaConnectionError(
            "Ollama is not running. Please start Ollama with: ollama serve\n"
            "Then ensure you have the embedding model: ollama pull nomic-embed-text"
        )

    # Process each chapter through pandoc
    chapters_html = []
    all_chunks = []

    for i, chapter in enumerate(config["chapters"]):
        chapter_folder = source_dir / chapter["folder"]
        chapter_file = chapter_folder / "content.md"

        if not chapter_file.exists():
            raise FileNotFoundError(f"Chapter file not found: {chapter_file}")

        # Read markdown content
        with open(chapter_file, 'r') as f:
            markdown_content = f.read()

        # Chunk the markdown content
        chapter_chunks = chunk_markdown(
            content=markdown_content,
            chapter_id=chapter["id"],
            max_tokens=500
        )
        all_chunks.extend(chapter_chunks)

        # Convert with pandoc for HTML display
        chapter_html = convert_markdown_to_html(chapter_file)

        # Wrap in chapter div (first chapter gets active class)
        active_class = " active" if i == 0 else ""
        wrapped_html = (
            f'<div class="chapter{active_class}" id="chapter-{chapter["id"]}">'
            f'\n{chapter_html}\n</div>'
        )
        chapters_html.append(wrapped_html)

    # Generate embeddings for all chunks
    print(f"Generating embeddings for {len(all_chunks)} chunks...")
    chunks_with_embeddings = generate_embeddings(
        chunks=all_chunks,
        model=config["embedding_model"],
        progress_callback=lambda cur, total: print(f"  Embedding {cur}/{total}...")
    )
    print("Embeddings complete.")

    # Generate TOC
    toc_html = generate_toc(config["chapters"])

    # Always generate chat widget (AI is mandatory)
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

    # Prepare chat config for Ollama
    chat_config = {
        "model": config["model"],
        "embedding_model": config["embedding_model"],
        "system_prompt": config["system_prompt"],
    }

    # Convert chunks to serializable format
    chunks_data = [chunk.to_dict() for chunk in chunks_with_embeddings]

    # Prepare template variables
    template_vars = {
        "title": config.get("title", "Book"),
        "author": config.get("author", ""),
        "toc_html": toc_html,
        "chapters_html": "\n".join(chapters_html),
        "chat_html": chat_html,
        "chunks_json": json.dumps(chunks_data),
        "chat_config_json": json.dumps(chat_config),
    }

    # Render template
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("book.html")
    output_html = template.render(**template_vars)

    # Write output files
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write HTML
    with open(output_file, 'w') as f:
        f.write(output_html)

    # Write chunks.json alongside HTML
    chunks_file = output_file.parent / "chunks.json"
    with open(chunks_file, 'w') as f:
        json.dump(chunks_data, f)

    print(f"Built: {output_file}")
    print(f"Chunks: {chunks_file} ({len(chunks_data)} chunks)")


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
