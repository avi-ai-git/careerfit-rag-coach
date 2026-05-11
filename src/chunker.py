# Splits documents into 700-character chunks with 100-char overlap for ChromaDB embedding.
# 700 chars keeps each chunk focused on one topic; 100-char overlap stops key phrases
# from disappearing because they happened to land at a chunk boundary.

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_core.documents import Document

from src.config import CHUNK_SIZE, CHUNK_OVERLAP, KB_DEMO_PATH


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split a list of Documents into smaller chunks for embedding and retrieval.

    RecursiveCharacterTextSplitter breaks on paragraph breaks first, then sentences,
    then words -- so chunks are coherent prose, not mid-sentence cuts.

    Each output chunk keeps all metadata from its source document plus:
      chunk_index (zero-based position within that source document)
      chunk_size_chars (character count, useful for debugging retrieval issues)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    all_chunks: list[Document] = []

    for doc in documents:
        raw_chunks = splitter.split_documents([doc])
        for idx, chunk in enumerate(raw_chunks):
            # split_documents copies source metadata; we add the chunk-specific fields here
            chunk.metadata["chunk_index"] = idx
            chunk.metadata["chunk_size_chars"] = len(chunk.page_content)
            all_chunks.append(chunk)

    return all_chunks


if __name__ == "__main__":
    from src.document_loader import load_documents

    docs = load_documents(KB_DEMO_PATH)
    chunks = chunk_documents(docs)

    print(f"Original documents : {len(docs)}")
    print(f"Total chunks       : {len(chunks)}")
    print()

    print("First 3 chunk previews:")
    for chunk in chunks[:3]:
        m = chunk.metadata
        preview = chunk.page_content[:80].replace("\n", " ")
        print(
            f"  source={m['source']!r}  doc_type={m['doc_type']!r}  "
            f"chunk_index={m['chunk_index']}  size={m['chunk_size_chars']} chars"
        )
        print(f"    preview: {preview!r}")
