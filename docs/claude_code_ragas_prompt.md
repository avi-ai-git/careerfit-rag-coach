# Claude Code Prompt: Add RAGAS Evaluation

Paste this into Claude Code to implement RAGAS evaluation alongside the existing source-hit evaluation.

---

## PROMPT (copy everything below this line)

---

This is the CareerFit RAG Coach project, a Turing College Sprint 2 LLM application.

It already has a source-hit evaluation in `src/evaluation.py` that checks whether the right knowledge base files are retrieved for 10 test questions. I want to add a second evaluation layer using RAGAS that measures answer quality, not just retrieval quality.

RAGAS measures four things:
- Faithfulness: did the generated answer only use facts from the retrieved context?
- Answer relevance: did the answer actually address the question asked?
- Context precision: were the retrieved chunks actually relevant to the question?
- Context recall: did retrieval get everything needed to answer the question?

Here is what I need you to do, in order.

---

### Step 1: Install RAGAS

Add these two lines to `requirements.txt` (keep them in alphabetical order with the existing packages):

```
datasets>=2.14.0
ragas>=0.1.0
```

Then run:

```bash
pip install ragas datasets
```

Tell me if any install errors occur before continuing.

---

### Step 2: Add ground truth answers to test_questions.json

Read `evaluation/test_questions.json`. It has 10 questions. Add a `ground_truth` field to each question. The ground truth is a 1 to 3 sentence description of what a correct, evidence-grounded answer should contain.

Here are the ground truth answers to use for each question ID:

q01: "The candidate designed and delivered the first English GenAI bootcamp in the state of Thuringia with 14 participants, facilitated 5 other AI education formats for 120+ total participants, and ran HIKEathon 2024 and 2025 coaching sessions for non-technical founders and students."

q02: "The candidate built a full-length AI short film selected for Artefact AI Film Festival Paris 2025, using Midjourney, Runway ML, ElevenLabs, and Adobe Premiere Pro, and has hands-on experience with 50+ AI tools documented in a structured prompt library."

q03: "The candidate has 4+ years of professional project management experience from TCS in Kolkata, covering agile delivery, stakeholder reporting, and cross-functional team coordination."

q04: "The candidate designed a 2-day GenAI bootcamp curriculum covering prompt engineering, tool selection, and AI workflow design, and delivered it to 14 participants with certificates issued. They also built the AI Bootcamp Prompt Engineering Knowledge Hub in Notion as a self-service resource."

q05: "The candidate uses Claude, ChatGPT, Midjourney, Runway ML, ElevenLabs, Gemini, Perplexity, and 50+ other AI tools professionally across writing, research, image generation, video generation, audio, and coding assistance categories."

q06: "The candidate reached 120+ participants across 6 AI education formats over 14 months. The #hikemussbleiben advocacy campaign contributed to securing 1.2 million euros in public funding for the StarTH network. LinkedIn grew to 1000+ followers and Instagram to 800+."

q07: "The candidate built a 50-tool AI prompt library in Notion covering writing, research, image generation, video, audio, coding, and productivity categories. This was delivered to bootcamp participants as the AI Bootcamp Prompt Engineering Knowledge Hub for self-service use after training ended."

q08: "The candidate holds an M.Sc. in Media Informatics from RWTH Aachen University and a Digital Marketing Diploma from CareerFoundry. They have completed Anthropic Claude Certification and are currently completing the Turing College LLM Application Development course."

q09: "The candidate grew an organization's LinkedIn to 1000+ followers and Instagram to 800+ followers, maintained a bilingual editorial calendar for 14 months, and produced the #hikemussbleiben advocacy campaign that contributed to securing 1.2 million euros in public funding."

q10: "The candidate explicitly does not target pure backend engineering, MLOps, production cloud infrastructure, or traditional marketing roles without an AI component. Technical depth in LangGraph multi-tool agent architecture and LangChain advanced features are listed as developing skills, not strong ones."

Write the updated test_questions.json with the ground_truth field added to each question. Keep all existing fields (id, question, expected_sources, expected_answer_theme).

---

### Step 3: Create src/ragas_evaluation.py

Create a new file at `src/ragas_evaluation.py`. Here is what it needs to do:

1. Load questions from `evaluation/test_questions.json`
2. For each question, run the full RAG pipeline to get a real answer and the retrieved chunks
3. Build a dataset RAGAS can evaluate
4. Run RAGAS metrics and print a summary
5. Save results to `evaluation/ragas_results.csv`

The file should follow the same pattern as `src/evaluation.py`. It needs a `run_ragas_evaluation()` function and a `if __name__ == "__main__":` block.

To get real answers and contexts for each question, you will need to call the tools directly rather than going through the full agent (the agent has overhead and memory that makes batch evaluation messy). Specifically:
- Call `translate_query(question)` from `src/query_translation.py` to get retrieval phrases
- Call `retrieve_chunks(phrase, exclude_doc_types=["test_job_descriptions"])` from `src/retriever.py` for each phrase
- Merge and deduplicate the chunks the same way `_search_impl()` in `src/tools.py` does it
- Call `format_context(chunks)` from `src/retriever.py` to get the context string
- Call `get_llm()` from `src/llm.py` and invoke it with a simple prompt: "Answer this question based only on the context below.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
- Collect: the question, the generated answer, the list of chunk content strings (contexts), and the ground_truth from the JSON

RAGAS needs a `datasets.Dataset` with columns: question, answer, contexts (list of strings), ground_truth.

Use these RAGAS metrics: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`.

RAGAS uses OpenAI by default. Configure it to use the OpenRouter endpoint by setting the RAGAS LLM to the same ChatOpenAI client that `src/llm.py` returns.

Print results as a readable table. Save to CSV. Handle errors gracefully: if RAGAS fails on one question (API error, timeout), log the error and continue.

---

### Step 4: Verify syntax

Run:

```bash
python -m py_compile src/ragas_evaluation.py && echo "OK"
```

If it fails, fix the error before continuing.

---

### Step 5: Test run (optional, costs API credits)

If I confirm, run:

```bash
python -m src.ragas_evaluation
```

This will make real LLM calls for each question (answer generation + RAGAS evaluation). Cost is roughly $0.05 to $0.10 total for 10 questions using gpt-4o-mini.

Wait for my confirmation before running this step.

---

### Done

Tell me what was added, what the file structure looks like, and what command I need to run to execute the RAGAS evaluation. Keep the summary short.
