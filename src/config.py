# Loads environment variables and defines all project-wide config constants and paths

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
KB_DEMO_PATH = PROJECT_ROOT / "knowledge_base_demo"
VECTORSTORE_DEMO_PATH = PROJECT_ROOT / "vectorstore_demo"

# Private KB paths are defined here so they can be dropped into vector_store.py
# if a private knowledge base is wired up. The directories are gitignored.
KB_PRIVATE_PATH = PROJECT_ROOT / "knowledge_base_private"
VECTORSTORE_PRIVATE_PATH = PROJECT_ROOT / "vectorstore_private"

# --- RAG tuning ---
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
RETRIEVAL_K = 7  # raised from 5 after adding 4 new KB files; more files = more competition per slot
COLLECTION_NAME = "careerfit_demo"

# --- LLM / API ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openai/gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def check_api_key() -> bool:
    """Return True if OPENROUTER_API_KEY is set, False otherwise. Never raises."""
    return bool(OPENROUTER_API_KEY)


if __name__ == "__main__":
    masked_key = (OPENROUTER_API_KEY[:8] + "...") if OPENROUTER_API_KEY else "(not set)"

    print("=== CareerFit RAG Coach Config ===")
    print(f"  PROJECT_ROOT:          {PROJECT_ROOT}")
    print(f"  KB_DEMO_PATH:          {KB_DEMO_PATH}")
    print(f"  KB_PRIVATE_PATH:       {KB_PRIVATE_PATH}")
    print(f"  VECTORSTORE_DEMO_PATH: {VECTORSTORE_DEMO_PATH}")
    print(f"  VECTORSTORE_PRIVATE_PATH: {VECTORSTORE_PRIVATE_PATH}")
    print()
    print(f"  CHUNK_SIZE:            {CHUNK_SIZE}")
    print(f"  CHUNK_OVERLAP:         {CHUNK_OVERLAP}")
    print(f"  RETRIEVAL_K:           {RETRIEVAL_K}")
    print()
    print(f"  OPENROUTER_API_KEY:    {masked_key}")
    print(f"  OPENROUTER_BASE_URL:   {OPENROUTER_BASE_URL}")
    print(f"  DEFAULT_MODEL:         {DEFAULT_MODEL}")
    print(f"  EMBEDDING_MODEL:       {EMBEDDING_MODEL}")
    print()
    print(f"  API key present:       {check_api_key()}")
