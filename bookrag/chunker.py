"""Chunk markdown content for RAG retrieval."""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    """A chunk of content for RAG retrieval."""
    id: str
    chapter_id: str
    heading: str
    content: str
    token_count: int


def estimate_tokens(text: str) -> int:
    """Estimate token count (roughly 4 chars per token)."""
    return len(text) // 4


def chunk_markdown(
    content: str,
    chapter_id: str,
    max_tokens: int = 500
) -> List[Chunk]:
    """Split markdown content into chunks for RAG.

    Chunks by headings (##, ###), then splits further by paragraph
    if a section exceeds max_tokens.

    Args:
        content: Markdown content to chunk
        chapter_id: ID of the chapter this content belongs to
        max_tokens: Maximum tokens per chunk (default 500)

    Returns:
        List of Chunk objects
    """
    chunks = []
    chunk_counter = 0

    # Split by headings (## or ###)
    # Pattern captures the heading line and everything until the next heading
    heading_pattern = r'^(#{2,3})\s+(.+?)$'

    # Find all headings and their positions
    headings = list(re.finditer(heading_pattern, content, re.MULTILINE))

    if not headings:
        # No headings - treat entire content as one section
        sections = [("", content.strip())]
    else:
        sections = []

        # Content before first heading
        first_heading_pos = headings[0].start()
        if first_heading_pos > 0:
            intro_content = content[:first_heading_pos].strip()
            if intro_content:
                sections.append(("Introduction", intro_content))

        # Process each heading and its content
        for i, match in enumerate(headings):
            heading_text = match.group(2).strip()

            # Get content between this heading and the next (or end)
            start = match.end()
            end = headings[i + 1].start() if i + 1 < len(headings) else len(content)
            section_content = content[start:end].strip()

            if section_content:
                sections.append((heading_text, section_content))

    # Process each section
    for heading, section_content in sections:
        section_tokens = estimate_tokens(section_content)

        if section_tokens <= max_tokens:
            # Section fits in one chunk
            chunk_counter += 1
            chunks.append(Chunk(
                id=f"{chapter_id}-{chunk_counter}",
                chapter_id=chapter_id,
                heading=heading,
                content=section_content,
                token_count=section_tokens
            ))
        else:
            # Section too large - split by paragraphs
            paragraphs = re.split(r'\n\n+', section_content)
            current_chunk_parts = []
            current_tokens = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                para_tokens = estimate_tokens(para)

                if current_tokens + para_tokens > max_tokens and current_chunk_parts:
                    # Save current chunk
                    chunk_counter += 1
                    chunks.append(Chunk(
                        id=f"{chapter_id}-{chunk_counter}",
                        chapter_id=chapter_id,
                        heading=heading,
                        content='\n\n'.join(current_chunk_parts),
                        token_count=current_tokens
                    ))
                    current_chunk_parts = []
                    current_tokens = 0

                # Handle very long paragraphs (> max_tokens)
                if para_tokens > max_tokens:
                    # Split by sentences as last resort
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        sent_tokens = estimate_tokens(sentence)

                        if current_tokens + sent_tokens > max_tokens and current_chunk_parts:
                            chunk_counter += 1
                            chunks.append(Chunk(
                                id=f"{chapter_id}-{chunk_counter}",
                                chapter_id=chapter_id,
                                heading=heading,
                                content='\n\n'.join(current_chunk_parts),
                                token_count=current_tokens
                            ))
                            current_chunk_parts = []
                            current_tokens = 0

                        current_chunk_parts.append(sentence)
                        current_tokens += sent_tokens
                else:
                    current_chunk_parts.append(para)
                    current_tokens += para_tokens

            # Save remaining content
            if current_chunk_parts:
                chunk_counter += 1
                chunks.append(Chunk(
                    id=f"{chapter_id}-{chunk_counter}",
                    chapter_id=chapter_id,
                    heading=heading,
                    content='\n\n'.join(current_chunk_parts),
                    token_count=current_tokens
                ))

    return chunks
