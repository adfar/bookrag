"""Tests for the chunker module."""
import pytest
from bookrag.chunker import chunk_markdown, estimate_tokens, Chunk


def test_estimate_tokens():
    """Test token estimation."""
    # ~4 chars per token
    assert estimate_tokens("hello world") == 2  # 11 chars -> 2 tokens
    assert estimate_tokens("") == 0
    assert estimate_tokens("a" * 100) == 25  # 100 chars -> 25 tokens


def test_chunk_simple_content():
    """Test chunking content without headings."""
    content = "This is a simple paragraph.\n\nThis is another paragraph."
    chunks = chunk_markdown(content, "intro")

    assert len(chunks) == 1
    assert chunks[0].chapter_id == "intro"
    assert chunks[0].id == "intro-1"
    assert "simple paragraph" in chunks[0].content


def test_chunk_by_headings():
    """Test chunking splits by ## headings."""
    content = """## Introduction
This is the intro content.

## Methods
This describes the methods.

## Results
These are the results.
"""
    chunks = chunk_markdown(content, "chapter1")

    assert len(chunks) == 3
    assert chunks[0].heading == "Introduction"
    assert chunks[1].heading == "Methods"
    assert chunks[2].heading == "Results"
    assert all(c.chapter_id == "chapter1" for c in chunks)


def test_chunk_preserves_content():
    """Test that chunking preserves all content."""
    content = """## Section One
Content for section one.

## Section Two
Content for section two.
"""
    chunks = chunk_markdown(content, "test")

    assert "Content for section one" in chunks[0].content
    assert "Content for section two" in chunks[1].content


def test_chunk_splits_large_sections():
    """Test that large sections are split by paragraphs."""
    # Create content that exceeds 500 tokens (~2000 chars)
    large_para = "This is a test sentence. " * 100  # ~2500 chars
    content = f"""## Large Section
{large_para}

Another paragraph here.
"""
    chunks = chunk_markdown(content, "large", max_tokens=500)

    # Should be split into multiple chunks
    assert len(chunks) > 1
    # All chunks should have the same heading
    assert all(c.heading == "Large Section" for c in chunks)


def test_chunk_content_before_headings():
    """Test that content before first heading is captured."""
    content = """This is intro content before any headings.

## First Section
Section content.
"""
    chunks = chunk_markdown(content, "test")

    assert len(chunks) == 2
    assert chunks[0].heading == "Introduction"
    assert "intro content" in chunks[0].content


def test_chunk_ids_are_unique():
    """Test that chunk IDs are unique within a chapter."""
    content = """## One
Content one.

## Two
Content two.

## Three
Content three.
"""
    chunks = chunk_markdown(content, "ch1")

    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))  # All unique


def test_chunk_handles_nested_headings():
    """Test handling of ### headings."""
    content = """## Main Section

### Subsection One
Subsection content.

### Subsection Two
More content.
"""
    chunks = chunk_markdown(content, "test")

    # Should capture all sections
    assert len(chunks) >= 2
    headings = [c.heading for c in chunks]
    assert "Subsection One" in headings
    assert "Subsection Two" in headings


def test_chunk_dataclass():
    """Test Chunk dataclass."""
    chunk = Chunk(
        id="test-1",
        chapter_id="test",
        heading="Test Heading",
        content="Test content",
        token_count=10
    )

    assert chunk.id == "test-1"
    assert chunk.chapter_id == "test"
    assert chunk.heading == "Test Heading"
    assert chunk.content == "Test content"
    assert chunk.token_count == 10
