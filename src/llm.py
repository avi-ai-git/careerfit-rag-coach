import os

from langchain_openai import ChatOpenAI

from src.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL


_OLLAMA_CLOUD_MODELS = {
    "gpt-oss:120b",
    "gpt-oss:20b",
    "gemma3:27b",
}


def get_llm(model: str = None, temperature: float = 0.2) -> ChatOpenAI:
    """Return a ChatOpenAI client for the given model.

    Routing:
      - Ollama Cloud models (e.g. 'gpt-oss:120b')  → OLLAMA_BASE_URL + OLLAMA_API_KEY
      - Everything else                              → OpenRouter
    """
    model = model or DEFAULT_MODEL

    if model in _OLLAMA_CLOUD_MODELS:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1/")
        ollama_key = os.getenv("OLLAMA_API_KEY", "")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=ollama_key,
            base_url=ollama_url,
        )

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


if __name__ == "__main__":
    llm = get_llm()
    response = llm.invoke(
        "Reply in exactly one sentence: the CareerFit pipeline is working."
    )
    print(response.content)
