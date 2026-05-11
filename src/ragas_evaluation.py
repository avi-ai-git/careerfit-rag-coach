# RAGAS answer-quality evaluation for CareerFit RAG Coach.
#
# Complements src/evaluation.py (which checks retrieval source hits) by measuring
# whether the generated answers are actually faithful, relevant, and grounded.
#
# Four metrics:
#   Faithfulness      -- does the answer only use facts from retrieved context?
#   Answer relevancy  -- does the answer address what was asked?
#   Context precision -- are the retrieved chunks actually relevant to the question?
#   Context recall    -- did retrieval surface enough to answer the ground truth?
#
# Run: python -m src.ragas_evaluation
# Cost: ~$0.05-0.10 total for 10 questions using gpt-4o-mini via OpenRouter.

import json
from pathlib import Path

from src.llm import get_llm
from src.logger import get_logger
from src.query_translation import translate_query
from src.retriever import format_context, retrieve_chunks

_log = get_logger("careerfit.ragas_eval")

_EVAL_DIR = Path(__file__).resolve().parent.parent / "evaluation"
_TEST_QUESTIONS_PATH = _EVAL_DIR / "test_questions.json"
_RESULTS_PATH = _EVAL_DIR / "ragas_results.csv"

# Simple QA prompt -- answers here are inputs to RAGAS, not shown to users.
# Kept short so the LLM doesn't pad the output with caveats that reduce faithfulness scores.
_QA_PROMPT = """\
Answer the question below using ONLY the information in the context provided.
Be specific. Cite numbers, names, and outcomes from the context where available.
Do not add information that is not in the context.

Context:
{context}

Question: {question}

Answer:"""


def _run_pipeline(question: str) -> dict:
    """Run query translation -> retrieval -> answer generation for one question.

    Mirrors _search_impl() in src/tools.py so the retrieval path is identical
    to what the agent uses in production. Returns the answer string and the
    list of retrieved chunk content strings that RAGAS needs for its metrics.
    """
    phrases = translate_query(question)

    # Multi-query retrieval with content-prefix deduplication (same as _search_impl)
    seen: set[str] = set()
    all_chunks: list[dict] = []
    for phrase in phrases:
        for chunk in retrieve_chunks(phrase, exclude_doc_types=["test_job_descriptions"]):
            key = chunk["content"][:100]
            if key not in seen:
                seen.add(key)
                all_chunks.append(chunk)

    context = format_context(all_chunks) if all_chunks else "No relevant evidence found."

    # contexts is a flat list of strings -- RAGAS expects list[str] per question
    contexts = [c["content"] for c in all_chunks] if all_chunks else ["No relevant evidence found."]

    llm = get_llm()
    prompt = _QA_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt)
    answer = response.content.strip()

    return {"answer": answer, "contexts": contexts}


def run_ragas_evaluation() -> list[dict]:
    """Generate answers for all questions, run RAGAS metrics, save and return results.

    RAGAS is configured to use the same OpenRouter LLM as the rest of the app so no
    additional API keys are needed. Local HuggingFace embeddings are reused for the
    answer_relevancy metric, which needs embeddings to score semantic similarity.
    """
    # Late imports so the module loads without error even when ragas isn't installed
    try:
        from datasets import Dataset
        from langchain_huggingface import HuggingFaceEmbeddings
        from ragas import evaluate
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
    except ImportError as exc:
        _log.error("RAGAS import failed: %s. Run: pip install ragas datasets", exc)
        raise

    questions = json.loads(_TEST_QUESTIONS_PATH.read_text(encoding="utf-8"))

    # Configure RAGAS to use the project's OpenRouter LLM instead of the default OpenAI.
    # LangchainLLMWrapper adapts any ChatOpenAI client to the RAGAS LLM interface.
    ragas_llm = LangchainLLMWrapper(get_llm())

    # answer_relevancy also needs an embedding model to score question-answer similarity.
    # Reuse the same local model the vector store uses -- no extra API calls or cost.
    hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    ragas_embeddings = LangchainEmbeddingsWrapper(hf_embeddings)

    # Collect rows for the Dataset
    data: dict[str, list] = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    print(f"\nGenerating answers for {len(questions)} questions...")
    for item in questions:
        qid = item["id"]
        question = item["question"]
        ground_truth = item.get("ground_truth", "")

        print(f"  [{qid}] {question[:65]}...")
        try:
            result = _run_pipeline(question)
            data["question"].append(question)
            data["answer"].append(result["answer"])
            data["contexts"].append(result["contexts"])
            data["ground_truth"].append(ground_truth)
            _log.info("%s: answer generated (%d chars)", qid, len(result["answer"]))
        except Exception as exc:
            _log.error("%s: pipeline failed: %s", qid, exc)
            # Keep the dataset aligned -- a blank answer still gets evaluated
            data["question"].append(question)
            data["answer"].append("Pipeline error: no answer generated.")
            data["contexts"].append(["No context retrieved."])
            data["ground_truth"].append(ground_truth)

    dataset = Dataset.from_dict(data)

    print(f"\nRunning RAGAS on {len(dataset)} samples (LLM calls per metric per question)...")
    ragas_result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=ragas_llm,
        embeddings=ragas_embeddings,
    )

    df = ragas_result.to_pandas()

    # Save full results (one row per question)
    _EVAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(_RESULTS_PATH, index=False, encoding="utf-8")
    _log.info("RAGAS results saved to %s", _RESULTS_PATH)

    return df.to_dict(orient="records")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    print("=" * 60)
    print("CareerFit RAG Coach -- RAGAS Answer Quality Evaluation")
    print("=" * 60)

    records = run_ragas_evaluation()

    print(f"\nResults saved to: {_RESULTS_PATH}")
    print("\nPer-question scores:")
    print(f"{'Q':<4}  {'Faithful':>9}  {'Relevancy':>9}  {'Ctx Prec':>8}  {'Ctx Recall':>10}")
    print("-" * 47)

    for i, r in enumerate(records, 1):
        faithful = r.get("faithfulness", float("nan"))
        relevancy = r.get("answer_relevancy", float("nan"))
        precision = r.get("context_precision", float("nan"))
        recall = r.get("context_recall", float("nan"))
        print(f"q{i:02d}   {faithful:>9.3f}  {relevancy:>9.3f}  {precision:>8.3f}  {recall:>10.3f}")

    # Compute and print averages
    import pandas as pd

    df = pd.DataFrame(records)
    metric_cols = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    print("\nAverages across all questions:")
    for col in metric_cols:
        if col in df.columns:
            avg = df[col].mean()
            bar = "█" * int(avg * 20)
            print(f"  {col:<22}: {avg:.3f}  {bar}")
