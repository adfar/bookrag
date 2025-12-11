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
