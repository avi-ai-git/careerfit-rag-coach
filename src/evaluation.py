# Manual RAG evaluation: checks whether expected source files appear in retrieved results

import csv
import json
from pathlib import Path

from src.retriever import retrieve_chunks

_EVAL_DIR = Path(__file__).resolve().parent.parent / "evaluation"
_TEST_QUESTIONS_PATH = _EVAL_DIR / "test_questions.json"
_RESULTS_PATH = _EVAL_DIR / "manual_eval_results.csv"


def run_evaluation() -> list[dict]:
    """Run source-hit evaluation for every question in test_questions.json.

    For each question:
      - Retrieve top-k chunks from ChromaDB.
      - Check whether every filename in expected_sources appears among the retrieved chunks.
      - Record source_hit (all expected present) and score (fraction present).

    Returns the list of result dicts and writes them to manual_eval_results.csv.
    """
    questions = json.loads(_TEST_QUESTIONS_PATH.read_text(encoding="utf-8"))
    results: list[dict] = []

    for item in questions:
        question: str = item["question"]
        expected: list[str] = item.get("expected_sources", [])

        chunks = retrieve_chunks(question, exclude_doc_types=["test_job_descriptions"])
        retrieved_sources: list[str] = sorted({c["source"] for c in chunks})

        hits = [src for src in expected if src in retrieved_sources]
        score = round(len(hits) / len(expected), 2) if expected else 0.0
        source_hit = len(hits) == len(expected) and bool(expected)

        results.append(
            {
                "question": question,
                "expected_sources": "|".join(expected),
                "retrieved_sources": "|".join(retrieved_sources),
                "source_hit": source_hit,
                "score": score,
            }
        )

    # Write CSV
    _EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with _RESULTS_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["question", "expected_sources", "retrieved_sources", "source_hit", "score"],
        )
        writer.writeheader()
        writer.writerows(results)

    return results


if __name__ == "__main__":
    print("Running RAG source-hit evaluation…\n")
    results = run_evaluation()

    total = len(results)
    hits = sum(1 for r in results if r["source_hit"])
    hit_rate = hits / total * 100 if total else 0.0

    print(f"Results saved to: {_RESULTS_PATH}\n")
    print(f"Total questions : {total}")
    print(f"Source hits     : {hits} / {total}  ({hit_rate:.0f}%)\n")

    failed = [r for r in results if not r["source_hit"]]
    if failed:
        print("Failed cases (expected source not retrieved):")
        for r in failed:
            print(f"  Q: {r['question'][:70]}")
            print(f"     expected : {r['expected_sources']}")
            print(f"     retrieved: {r['retrieved_sources']}")
            print(f"     score    : {r['score']}")
            print()
    else:
        print("All expected sources were retrieved successfully.")
