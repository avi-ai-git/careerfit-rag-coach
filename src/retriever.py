# Retrieves chunks from ChromaDB -- k raised to 7 after adding 4 new case study files;
# k=5 was too narrow once the knowledge base grew past 9 files.

from langchain_chroma import Chroma

from src.config import RETRIEVAL_K
from src.vector_store import load_vector_store

# loaded once per process; reloading on every call added ~200ms latency
_vector_store: Chroma | None = None


def _get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        _vector_store = load_vector_store()
    return _vector_store


def retrieve_chunks(query: str, k: int = None, exclude_doc_types: list[str] | None = None) -> list[dict]:
    """Run a similarity search and return the top-k chunks as plain dicts.

    Each dict has: content, source (filename), doc_type, score (0-1).
    exclude_doc_types lets callers filter out specific doc categories after retrieval
    rather than before -- ChromaDB metadata filtering exists but adds query complexity.
    """
    k = k if k is not None else RETRIEVAL_K
    vs = _get_vector_store()
    results = vs.similarity_search_with_relevance_scores(query, k=k)

    chunks = []
    for doc, score in results:
        chunks.append(
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "doc_type": doc.metadata.get("doc_type", "unknown"),
                "score": round(score, 4),
            }
        )

    # test_job_descriptions chunks exist for QA testing only --
    # letting them compete in real career queries buries the actual case study files
    if exclude_doc_types:
        chunks = [c for c in chunks if c["doc_type"] not in exclude_doc_types]

    return chunks


def format_context(chunks: list[dict]) -> str:
    """Format a list of chunks into a context block for prompt injection.

    Source labels use the actual filename rather than a numbered "Source N" prefix.
    Numbered prefixes caused the LLM to cite 'source_3.md' instead of the real filename.
    """
    parts = []
    for chunk in chunks:
        parts.append(
            f"--- FILE: {chunk['source']} ({chunk['doc_type']}) ---"
        )
        parts.append(chunk["content"])
        parts.append("")  # blank line between chunks
    return "\n".join(parts).strip()


if __name__ == "__main__":
    query = "What evidence shows experience with AI education and bootcamp delivery?"
    print(f"Query: {query!r}\n")

    results = retrieve_chunks(query, k=3)
    for i, chunk in enumerate(results, 1):
        print(f"Result {i}")
        print(f"  source   : {chunk['source']}")
        print(f"  doc_type : {chunk['doc_type']}")
        print(f"  score    : {chunk['score']}")
        print(f"  preview  : {chunk['content'][:120].replace(chr(10), ' ')!r}")
        print()
