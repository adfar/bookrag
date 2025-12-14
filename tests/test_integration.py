import pytest
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch, Mock
from bookrag.builder import build_book

# Check if pandoc is installed
PANDOC_AVAILABLE = shutil.which("pandoc") is not None


@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not installed")
def test_build_sample_book(tmp_path: Path) -> None:
    """Test building complete book from sample fixture."""
    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    # Mock Ollama availability and embedding generation
    with patch('bookrag.builder.check_ollama_available', return_value=True), \
         patch('bookrag.builder.generate_embeddings') as mock_embed:
        # Return mock chunks with embeddings
        mock_embed.return_value = [
            Mock(to_dict=lambda: {
                "id": "intro-1",
                "chapter_id": "intro",
                "heading": "Introduction",
                "content": "Test content",
                "token_count": 10,
                "embedding": [0.1, 0.2, 0.3]
            })
        ]

        build_book(source_dir, output_file)

    # Verify output exists
    assert output_file.exists()

    # Verify chunks.json was created
    chunks_file = tmp_path / "chunks.json"
    assert chunks_file.exists()

    # Verify HTML content
    html_content = output_file.read_text()
    assert '<title>Sample Book</title>' in html_content
    assert 'Introduction' in html_content
    assert 'Chapter 1' in html_content
    assert 'This is the introduction chapter' in html_content
    # Always 3-column layout with chat (AI is mandatory)
    assert 'class="book-container"' in html_content
    assert 'chat-widget' in html_content
    assert 'AI Assistant' in html_content
    assert 'chapter-intro' in html_content
    assert 'chapter-chapter1' in html_content
    # Verify Ollama config is embedded
    assert 'llama3.2' in html_content
    assert 'localhost:11434' in html_content
    # Verify chunks are embedded
    assert 'CHUNKS' in html_content


def test_pandoc_not_installed(tmp_path: Path, monkeypatch) -> None:
    """Test graceful error when pandoc not installed."""
    def mock_run(*args, **kwargs):
        raise FileNotFoundError("pandoc not found")

    monkeypatch.setattr(subprocess, "run", mock_run)

    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    # Mock Ollama availability
    with patch('bookrag.builder.check_ollama_available', return_value=True):
        with pytest.raises(FileNotFoundError, match="Pandoc not found"):
            build_book(source_dir, output_file)


def test_ollama_not_running(tmp_path: Path) -> None:
    """Test graceful error when Ollama not running."""
    from bookrag.embeddings import OllamaConnectionError

    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    with patch('bookrag.builder.check_ollama_available', return_value=False):
        with pytest.raises(OllamaConnectionError, match="Ollama is not running"):
            build_book(source_dir, output_file)
