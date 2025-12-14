"""Tests for the embeddings module."""
import pytest
from unittest.mock import patch, Mock
from bookrag.chunker import Chunk
from bookrag.embeddings import (
    generate_embedding,
    generate_embeddings,
    check_ollama_available,
    ChunkWithEmbedding,
    OllamaConnectionError
)


def test_chunk_with_embedding_to_dict():
    """Test ChunkWithEmbedding serialization."""
    chunk = ChunkWithEmbedding(
        id="test-1",
        chapter_id="test",
        heading="Test",
        content="Test content",
        token_count=10,
        embedding=[0.1, 0.2, 0.3]
    )

    d = chunk.to_dict()
    assert d["id"] == "test-1"
    assert d["embedding"] == [0.1, 0.2, 0.3]


def test_generate_embedding_connection_error():
    """Test error handling when Ollama is not running."""
    with patch('bookrag.embeddings.requests.post') as mock_post:
        mock_post.side_effect = Exception("Connection refused")
        # Use ConnectionError specifically
        import requests
        mock_post.side_effect = requests.ConnectionError()

        with pytest.raises(OllamaConnectionError, match="Cannot connect to Ollama"):
            generate_embedding("test text")


def test_generate_embedding_model_not_found():
    """Test error handling when model is not installed."""
    with patch('bookrag.embeddings.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="not found"):
            generate_embedding("test text", model="nonexistent-model")


def test_generate_embedding_success():
    """Test successful embedding generation."""
    with patch('bookrag.embeddings.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        mock_post.return_value = mock_response

        result = generate_embedding("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_post.assert_called_once()


def test_generate_embeddings_multiple_chunks():
    """Test embedding generation for multiple chunks."""
    chunks = [
        Chunk(id="ch1-1", chapter_id="ch1", heading="Intro", content="Content 1", token_count=10),
        Chunk(id="ch1-2", chapter_id="ch1", heading="Methods", content="Content 2", token_count=10),
    ]

    with patch('bookrag.embeddings.generate_embedding') as mock_embed:
        mock_embed.side_effect = [[0.1, 0.2], [0.3, 0.4]]

        result = generate_embeddings(chunks)

        assert len(result) == 2
        assert result[0].embedding == [0.1, 0.2]
        assert result[1].embedding == [0.3, 0.4]
        assert result[0].id == "ch1-1"
        assert result[1].id == "ch1-2"


def test_generate_embeddings_with_progress_callback():
    """Test progress callback is called."""
    chunks = [
        Chunk(id="ch1-1", chapter_id="ch1", heading="A", content="C1", token_count=5),
        Chunk(id="ch1-2", chapter_id="ch1", heading="B", content="C2", token_count=5),
    ]

    progress_calls = []

    def progress_cb(current, total):
        progress_calls.append((current, total))

    with patch('bookrag.embeddings.generate_embedding') as mock_embed:
        mock_embed.return_value = [0.1, 0.2]

        generate_embeddings(chunks, progress_callback=progress_cb)

        assert progress_calls == [(1, 2), (2, 2)]


def test_check_ollama_available_success():
    """Test Ollama availability check when running."""
    with patch('bookrag.embeddings.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.ok = True
        mock_get.return_value = mock_response

        assert check_ollama_available() is True


def test_check_ollama_available_not_running():
    """Test Ollama availability check when not running."""
    with patch('bookrag.embeddings.requests.get') as mock_get:
        import requests
        mock_get.side_effect = requests.ConnectionError()

        assert check_ollama_available() is False
