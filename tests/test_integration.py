import pytest
import shutil
import subprocess
from pathlib import Path
from bookrag.builder import build_book

# Check if pandoc is installed
PANDOC_AVAILABLE = shutil.which("pandoc") is not None


@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not installed")
def test_build_sample_book(tmp_path: Path) -> None:
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
    # Always 3-column layout with chat (AI is mandatory)
    assert 'class="book-container"' in html_content
    assert 'chat-widget' in html_content
    assert 'AI Assistant' in html_content
    assert 'chapter-intro' in html_content
    assert 'chapter-chapter1' in html_content
    # Verify Ollama config is embedded
    assert 'llama3.2' in html_content
    assert 'localhost:11434' in html_content


def test_pandoc_not_installed(tmp_path: Path, monkeypatch) -> None:
    """Test graceful error when pandoc not installed."""
    def mock_run(*args, **kwargs):
        raise FileNotFoundError("pandoc not found")

    monkeypatch.setattr(subprocess, "run", mock_run)

    source_dir = Path(__file__).parent / "fixtures" / "sample-book"
    output_file = tmp_path / "output.html"

    with pytest.raises(FileNotFoundError, match="Pandoc not found"):
        build_book(source_dir, output_file)
