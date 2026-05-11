# Builds and persists a ChromaDB vector store from document chunks

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.config import (
    EMBEDDING_MODEL,
    KB_DEMO_PATH,
    VECTORSTORE_DEMO_PATH,
    COLLECTION_NAME,
)
from src.document_loader import load_documents
from src.chunker import chunk_documents


def get_embedding_function() -> HuggingFaceEmbeddings:
    """Return a local sentence-transformers embedding function.

    Uses the model name defined in src.config.EMBEDDING_MODEL.
    No external API calls are made.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vector_store(
    chunks: list[Document] | None = None,
    persist_dir: str | Path = VECTORSTORE_DEMO_PATH,
    collection_name: str = COLLECTION_NAME,
) -> Chroma:
    """Embed chunks and persist them to a ChromaDB collection.

    If chunks is None, the function loads and chunks KB_DEMO_PATH automatically.

    The persist_dir is deleted and recreated on each call so that repeated
    runs do not accumulate duplicate embeddings.

    Returns the Chroma vector store object.
    """
    persist_dir = Path(persist_dir)

    # Load and chunk if no chunks supplied
    if chunks is None:
        docs = load_documents(KB_DEMO_PATH)
        chunks = chunk_documents(docs)

    # Wipe existing store to avoid duplicates on repeated runs
    if persist_dir.exists():
        shutil.rmtree(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embedding_fn = get_embedding_function()

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_fn,
        collection_name=collection_name,
        persist_directory=str(persist_dir),
    )

    return vector_store


def load_vector_store(
    persist_dir: str | Path = VECTORSTORE_DEMO_PATH,
    collection_name: str = COLLECTION_NAME,
) -> Chroma:
    """Load an existing ChromaDB collection from disk and return it.

    Raises FileNotFoundError if persist_dir does not exist.
    """
    persist_dir = Path(persist_dir)
    if not persist_dir.exists():
        raise FileNotFoundError(
            f"Vector store directory not found: {persist_dir}\n"
            "Run build_vector_store() first."
        )

    embedding_fn = get_embedding_function()

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_fn,
        persist_directory=str(persist_dir),
    )

    return vector_store


if __name__ == "__main__":
    # --- Load raw documents ---
    docs = load_documents(KB_DEMO_PATH)
    print(f"Loaded documents  : {len(docs)}")

    # --- Chunk ---
    chunks = chunk_documents(docs)
    print(f"Total chunks      : {len(chunks)}")

    # --- Build vector store ---
    print(f"\nBuilding vector store at: {VECTORSTORE_DEMO_PATH}")
    print(f"Collection name   : {COLLECTION_NAME}")
    vs = build_vector_store(chunks=chunks)
    print("Vector store built successfully.")

    # --- First 3 source filenames from chunks ---
    print("\nFirst 3 chunk sources:")
    for chunk in chunks[:3]:
        print(f"  {chunk.metadata['source']!r}")

    # --- Collection count ---
    try:
        count = vs._collection.count()
        print(f"\nDocuments in collection: {count}")
    except Exception as exc:
        print(f"\nCould not retrieve collection count: {exc}")
