# Expands a user query into multiple retrieval phrases before hitting ChromaDB.
# Using the LLM to paraphrase is slower than direct search but significantly
# improves recall when the user's phrasing doesn't match KB document vocabulary.
# model parameter propagates the user's sidebar selection so the full pipeline
# uses one consistent model rather than silently falling back to DEFAULT_MODEL.

import re

from src.llm import get_llm
from src.logger import get_logger

_log = get_logger("careerfit.query_translation")

_PROMPT_TEMPLATE = """\
You are a retrieval query optimizer for a RAG career coaching system.

The knowledge base contains a candidate's CV, skills inventory, career goals, \
education, case studies, and application examples.

Given the user input below, generate 3 to 5 short search queries optimized for \
vector similarity search over that knowledge base. Each query should be a \
standalone phrase or sentence, not a question.

Focus on extracting:
- Specific skills and tools mentioned
- Role requirements and responsibilities
- Domain keywords and industry terms
- Achievements or proof points relevant to the input

Return ONLY the queries as a numbered list (e.g. "1. query text"), one per line. \
No explanations, no preamble.

User input:
{user_input}
"""


def translate_query(user_input: str, model: str = None) -> list[str]:
    """Send user_input to the LLM and get back 3-5 retrieval-optimized phrases.

    model accepts the user's sidebar selection so the query expansion step uses
    the same model as the rest of the pipeline. Defaults to DEFAULT_MODEL when
    None is passed (e.g. from the __main__ test block or older callers).
    Falls back to [user_input] on any failure so the pipeline never breaks,
    just degrades to single-query retrieval.
    Temperature is 0.3 rather than 0.2 to get more phrase variety across queries.
    """
    try:
        llm = get_llm(model=model, temperature=0.3)
        response = llm.invoke(_PROMPT_TEMPLATE.format(user_input=user_input))
        lines = response.content.strip().splitlines()

        queries: list[str] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # strip leading "1." / "1)" / "- " markers that models like to add
            line = re.sub(r"^[\d]+[\.\)]\s*", "", line)
            line = re.sub(r"^[-*]\s*", "", line)
            if line:
                queries.append(line)

        return queries if queries else [user_input]

    except Exception as exc:
        _log.warning("query translation failed (%s), falling back to original query", exc)
        return [user_input]


if __name__ == "__main__":
    user_input = (
        "We need someone with experience designing and delivering AI training "
        "programs for non-technical audiences, ideally in an international NGO "
        "or development sector context."
    )

    print(f"Original input:\n  {user_input}\n")
    queries = translate_query(user_input)
    print(f"Translated into {len(queries)} retrieval queries:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
