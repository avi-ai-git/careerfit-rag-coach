# Display helpers tested in tests/test_core.py and available for use in the app.


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Shorten text to max_chars and append a truncation marker."""
    if len(text) > max_chars:
        return text[:max_chars] + "... [truncated]"
    return text


def format_sources(chunks: list) -> str:
    """Return a deduplicated, sorted list of source filenames from a chunk list."""
    unique_sources = sorted({c["source"] for c in chunks})
    return "\n".join(f"- {src}" for src in unique_sources)
