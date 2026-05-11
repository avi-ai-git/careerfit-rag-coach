# Claude Code Prompt — CareerFit RAG Coach Final Fixes

Paste this prompt into Claude Code to complete the remaining tasks before submission.

---

## PROMPT (copy everything below this line)

---

This is the CareerFit RAG Coach project — a Turing College Sprint 2 LLM application. It is a career coaching tool that uses RAG (ChromaDB + sentence-transformers + LangChain + LangGraph) to ground all AI outputs in a structured knowledge base of the candidate's documented career experience.

I need you to do the following tasks in order. Read each file before editing it. Do not change any logic — only the changes listed below.

---

### Task 1: Rebuild the vectorstore

The knowledge base was updated: 4 new case study files were added, 2 existing files were rewritten, and the old sprint1_project.md was deleted. The vectorstore on disk is stale and does not include any of the new content. Run:

```bash
python -m src.vector_store
```

Wait for it to complete. It will print the number of chunks. The expected chunk count is roughly 130–160. If it prints an error, tell me what the error says before continuing.

---

### Task 2: Run the evaluation

After the vectorstore is rebuilt, run:

```bash
python -m src.evaluation
```

This runs 10 test questions against ChromaDB and writes results to `evaluation/manual_eval_results.csv`. Tell me the hit rate it prints (e.g. "Source hits: 8 / 10 (80%)"). If any questions still fail, tell me which ones and which expected source was not retrieved.

---

### Task 3: Verify document_loader.py is correct

Read `src/document_loader.py`. Check that `_DOC_TYPE_MAP` contains entries for all of the following files and NO entries for deleted/moved files:

Expected entries:
- cv_summary.md → "cv_summary"
- skills_inventory.md → "skills_inventory"
- career_goals.md → "career_goals"
- career_principles.md → "career_principles"
- education.md → "education"
- hike_case_study.md → "case_study"
- giz_case_study.md → "case_study"
- ai_interview_app_case_study.md → "case_study"
- ctrl_alt_deity_case_study.md → "case_study"
- farout_case_study.md → "case_study"
- application_examples.md → "application_examples"

Should NOT be present:
- sprint1_project.md (this file was deleted)
- example_job_descriptions.md (this file was moved to evaluation/ and is no longer in knowledge_base_demo/)

If the map already matches this, say so and move on. If it does not, make the correction.

---

### Task 4: Run the automated tests

Run:

```bash
python -m pytest tests/ -v
```

Tell me which tests pass and which fail. If any fail, read the test file at `tests/test_core.py` and tell me what is being tested and what the error is. Do not fix test failures without explaining them to me first.

---

### Task 5: Check for em dashes in app.py

Run:

```bash
python -c "
content = open('app.py', encoding='utf-8').read()
lines = content.splitlines()
for i, line in enumerate(lines, 1):
    if '—' in line:
        print(f'Line {i}: {line.strip()[:80]}')
"
```

If any em dashes are found, show me each line. Then replace every em dash in app.py with a colon, a comma, or rewrite the phrase in plain language — whichever reads most naturally for that specific line. Do not make any other changes to app.py.

---

### Task 6: Final syntax check

Run:

```bash
python -m py_compile app.py && echo "app.py OK"
python -m py_compile src/agent.py && echo "agent.py OK"
python -m py_compile src/tools.py && echo "tools.py OK"
python -m py_compile src/retriever.py && echo "retriever.py OK"
python -m py_compile src/document_loader.py && echo "document_loader.py OK"
python -m py_compile src/security.py && echo "security.py OK"
```

All six must print OK. If any fail, show me the error and fix it.

---

### Done

After all six tasks are complete, give me a one-paragraph summary of what you did, the hit rate from the evaluation, and whether all syntax checks passed. Keep it short.
