"""Generate embeddings via Ollama for RAG retrieval."""
import requests
from dataclasses import dataclass
from typing import List
from bookrag.chunker import Chunk


@dataclass
class ChunkWithEmbedding:
    """A chunk with its embedding vector."""
    id: str
    chapter_id: str
    heading: str
    content: str
    token_count: int
    embedding: List[float]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "heading": self.heading,
            "content": self.content,
            "token_count": self.token_count,
            "embedding": self.embedding
        }


class OllamaConnectionError(Exception):
    """Raised when Ollama is not running or unreachable."""
    pass


def generate_embedding(
    text: str,
    model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434"
) -> List[float]:
    """Generate embedding for a single text using Ollama.

    Args:
        text: Text to embed
        model: Ollama embedding model (default: nomic-embed-text)
        base_url: Ollama server URL

    Returns:
        Embedding vector as list of floats

    Raises:
        OllamaConnectionError: If Ollama is not running
        ValueError: If embedding generation fails
    """
    try:
        response = requests.post(
            f"{base_url}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=30
        )
    except requests.ConnectionError:
        raise OllamaConnectionError(
            f"Cannot connect to Ollama at {base_url}. "
            "Please ensure Ollama is running: ollama serve"
        )
    except requests.Timeout:
        raise OllamaConnectionError(
            f"Timeout connecting to Ollama at {base_url}. "
            "The embedding model may be loading - try again."
        )

    if response.status_code == 404:
        raise ValueError(
            f"Embedding model '{model}' not found. "
            f"Install it with: ollama pull {model}"
        )

    if not response.ok:
        raise ValueError(
            f"Ollama embedding failed: {response.status_code} {response.text}"
        )

    data = response.json()
    if "embedding" not in data:
        raise ValueError(f"Invalid Ollama response: {data}")

    return data["embedding"]


def generate_embeddings(
    chunks: List[Chunk],
    model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
    progress_callback=None
) -> List[ChunkWithEmbedding]:
    """Generate embeddings for all chunks using Ollama.

    Args:
        chunks: List of Chunk objects to embed
        model: Ollama embedding model (default: nomic-embed-text)
        base_url: Ollama server URL
        progress_callback: Optional callback(current, total) for progress

    Returns:
        List of ChunkWithEmbedding objects

    Raises:
        OllamaConnectionError: If Ollama is not running
        ValueError: If embedding generation fails
    """
    result = []

    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(i + 1, len(chunks))

        embedding = generate_embedding(chunk.content, model, base_url)

        result.append(ChunkWithEmbedding(
            id=chunk.id,
            chapter_id=chunk.chapter_id,
            heading=chunk.heading,
            content=chunk.content,
            token_count=chunk.token_count,
            embedding=embedding
        ))

    return result


def check_ollama_available(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible.

    Args:
        base_url: Ollama server URL

    Returns:
        True if Ollama is running, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.ok
    except (requests.ConnectionError, requests.Timeout):
        return False
