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

    config_content = """title: "AI-Enabled Book"
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
