# CareerFit RAG Coach

A career coaching tool that reads a job description and tells you how well you fit it, what to lead with, and how to prepare for the interview. Every answer is grounded in a structured knowledge base of the candidate's real documented experience. If the evidence is not there, the app says so instead of making something up.

---

## The idea

I kept running into the same problem with AI writing tools: they generate confident-sounding career content that has nothing to do with your actual background. The output sounds good but the claims are either invented or so generic they could apply to anyone.

This app flips that. Instead of prompting an LLM with a blank canvas, it first searches a structured knowledge base of the candidate's documented experience, retrieves the most relevant passages, and only then asks the LLM to write something. The LLM is explicitly instructed not to use anything outside what retrieval returned. That constraint is what makes the output trustworthy rather than plausible-sounding.

---

## What it does

Paste a job description and choose a mode:

**Analyze Job Fit** gives you a fit score from 0 to 100, a breakdown of matched strengths (each cited to a source file), and an honest list of gaps the JD requires but the profile does not support.

**Application Positioning** drafts a positioning paragraph you can adapt for a cover letter, five specific proof points with citations, and a list of claims the evidence does not support (so you know what not to say).

**Interview Prep** generates ten likely interview questions for the role with STAR-format answer notes, each citing the knowledge base file the answer comes from.

**Ask Career Base** is a freeform mode for questions like "what can I point to for a content strategy role?" without needing a full job description.

---

## How it works

The knowledge base is 11 markdown files covering the candidate's CV, skills, education, case studies, career goals, and application examples. Before the app launches, those files are chunked into 144 pieces and embedded into a ChromaDB vector database using a local sentence-transformers model. No external API is called during that step.

When a user submits a query:

1. Input validation runs first. Length is checked (20 to 15,000 characters). If `MISTRAL_API_KEY` is set, Mistral Moderation runs as a hard block for harmful content and multilingual injection. A semantic LLM call then classifies the input as career-related or suspicious. A phrase list catches known jailbreak patterns with a soft warning.

2. The LangGraph ReAct agent receives the query and decides which tool to call based on the mode.

3. The tool runs query translation: it sends the user's query to the LLM and asks for 3 to 5 shorter retrieval-optimized phrases. This bridges the vocabulary gap between how people phrase questions and how the knowledge base documents are written.

4. Each translated phrase runs as a separate ChromaDB similarity search. The top 7 chunks per phrase are merged and deduplicated. Any chunk tagged as test data is filtered out before the results are used.

5. The retrieved chunks are formatted into a labeled context block and injected into a structured prompt template along with the original query.

6. The LLM generates a response constrained to that retrieved context. Source filenames are cited inline.

7. The response appears in the UI with a sources expander showing which tools were called, which model was used, and the estimated token cost.

Multi-turn memory works within a browser session via LangGraph's MemorySaver. A page reload resets it.

---

## Tech stack

**Streamlit** for the UI. No frontend build step, fast to iterate on, and the session state model works well for a single-user tool.

**LangGraph** for the agent. The ReAct loop (reason, pick a tool, observe the result, repeat or respond) is more flexible than a static chain when the agent might need to call tools in different combinations depending on the input.

**LangChain** for document loading, text splitting, and retrieval abstractions.

**ChromaDB** for the vector store. Persists to disk, no external service, no ongoing cost, and has a clean LangChain integration with metadata filtering support.

**sentence-transformers/all-MiniLM-L6-v2** for embeddings. Runs locally, no API calls, no cost per query. The model is about 90 MB and downloads on first use.

**OpenRouter** as the LLM gateway. One API key covers GPT-4o, Claude, Gemini, DeepSeek, and others without needing separate SDK setups for each provider.

**Ollama** (optional) for running local or cloud-hosted open-source models when `OLLAMA_BASE_URL` is set in the environment.

---

## Knowledge base

```
knowledge_base_demo/
    cv_summary.md               work history, tools, role titles
    skills_inventory.md         skill ratings (Strong, Developing, Limited) and explicit non-claims
    education.md                degrees, certifications, ongoing courses
    career_goals.md             target roles, geography, salary range, what is not being targeted
    career_principles.md        the organizing logic behind career decisions
    application_examples.md     positioning templates and tone examples
    hike_case_study.md          AI education lead role at HIKE startup incubator
    giz_case_study.md           GIZ internship, LMS redesign, 30% engagement lift
    ai_interview_app_case_study.md   Sprint 1 app, external security review, live URL
    ctrl_alt_deity_case_study.md     AI short film selected for Artefact AI Film Festival Paris 2025
    farout_case_study.md        NASA data visualization app built for Replit Buildathon
```

Files are split at 700 characters with 100-character overlap, producing 144 chunks total. Each chunk carries its source filename and a doc_type label as metadata. The doc_type label is how the retriever filters out test data from career query results.

```
evaluation/
    example_job_descriptions.md     test JDs for manual QA, not retrieved in production
    test_questions.json             10 evaluation questions with expected source files
    manual_eval_results.csv         results from the last evaluation run
```

`example_job_descriptions.md` was originally in the knowledge base directory. Its broad vocabulary was crowding out real career files in search results (the retrieval sponge problem). Moving it to `evaluation/` and adding an `exclude_doc_types` filter in the retriever fixed that.

---

## Evaluation

Two evaluation layers are implemented, covering different parts of the pipeline.

### Retrieval source hits (layer 1)

Runs 10 test questions against ChromaDB and checks whether the expected source files appear in the results. A source hit means every expected file was found; a miss means at least one was not.

The test questions are written to use vocabulary that appears in the target files. This is deliberate: if a question uses generic terms like "metrics" but the KB file uses specific terms like "120+ participants" and "€1.2M funding," the vector search will score them lower than a question that uses the same specific language. Good evaluation questions match the way the content is actually written.

Hit rate target: 90% or above (9 of 10 questions). Results are written to `evaluation/manual_eval_results.csv`.

```bash
python -m src.evaluation
```

### Answer quality with RAGAS (layer 2)

Runs the same 10 questions through the full pipeline (query translation, retrieval, and LLM answer generation) and uses RAGAS to score the output across four metrics:

- **Faithfulness:** does the answer only assert facts from the retrieved context?
- **Answer relevancy:** does the answer actually address what was asked?
- **Context precision:** are the retrieved chunks genuinely relevant to the question?
- **Context recall:** did retrieval surface enough content to answer correctly?

RAGAS uses the same OpenRouter LLM and local HuggingFace embeddings as the rest of the app, so no additional API keys are needed. A full 10-question run costs roughly $0.05 to $0.10 using gpt-4o-mini. Results are saved to `evaluation/ragas_results.csv`.

```bash
python -m src.ragas_evaluation
```

---

## Optional tools

Two tools are off by default and toggled on in the sidebar.

**Company research** uses DuckDuckGo's instant answer API to pull a short public summary of a company when the user names one. No API key needed. Works well for large global companies; returns sparse results for most regional European companies. The agent is instructed to call this first whenever a company name appears in the input, before doing anything else.

**Live job search** calls the Adzuna Jobs API for up to 5 live listings matching a role title in Berlin. Requires `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` in `.env` (free tier at developer.adzuna.com). Only available in Ask Career Base mode because in the three JD modes the user already has a job description and searching for listings adds noise.

---

## Known limitations

**Memory resets on page reload.** LangGraph MemorySaver is stored in session state. Multi-turn context works within a session but disappears on refresh. The drop-in fix is LangGraph SqliteSaver, which persists to a local file.

**RAGAS evaluation needs an API key.** The answer-quality evaluation layer uses OpenRouter to judge each response. It will fail silently if `OPENROUTER_API_KEY` is not set. Run it locally rather than on Streamlit Cloud.

**DuckDuckGo company search is sparse.** This is a data availability issue, not a code bug. Most German regional companies have limited indexing on DDG. The agent falls back gracefully to KB-only evidence when the tool returns nothing.

**Single-user architecture.** No auth, no multi-tenancy. The session rate limit (50 requests, 3-second cooldown) prevents accidental button spam in a demo context but is not a production access control.

**LangGraph `create_react_agent` deprecation.** The import from `langgraph.prebuilt` works in the current version but is scheduled for removal in LangGraph v2.0. Migration is a one-line change that has been deferred.

---

## Sprint 1 to Sprint 2 improvements

Sprint 1 was a direct LLM app: user types, LLM responds. No retrieval, no grounding, no memory, no validation, no evaluation. It worked and it deployed, but the output could not be trusted because it had no connection to real evidence.

Sprint 2 added the whole grounding layer:

| What changed | How |
|---|---|
| Retrieval grounding | ChromaDB vectorstore with sentence-transformers embeddings |
| Query improvement | LLM rewrites each query into 3 to 5 retrieval phrases before searching |
| Agent architecture | LangGraph ReAct agent with tool selection instead of a static chain |
| Conversation memory | MemorySaver keeps context across turns in the same session |
| Input security | Four-layer validation: length, Mistral Moderation (optional), LLM semantic check, phrase list |
| Cost tracking | tiktoken estimation per query, shown in the UI |
| Evaluation | Source-hit framework + RAGAS answer quality scoring, 10 test questions |
| Multiple models | 3 OpenRouter models and 3 Ollama Cloud models selectable in sidebar |
| Optional MCP tools | Company research and job search, off by default |
| Structured outputs | Fixed markdown format with mandatory source citations |
| Logging | Named loggers with timestamps across all modules |
| Tests | Automated tests covering security, cost tracking, doc loading, and utilities |

---

## Setup

You need Python 3.10 or above and an OpenRouter API key.

```bash
# clone and enter the project
git clone https://github.com/avi-ai-git/careerfit-rag-coach.git
cd careerfit-rag-coach

# create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS and Linux

# install dependencies
pip install -r requirements.txt

# set up your API key
copy .env.example .env        # Windows
cp .env.example .env          # macOS and Linux
# open .env and set OPENROUTER_API_KEY=your-key-here

# build the vector store (downloads ~90 MB model on first run)
python -m src.vector_store

# start the app
streamlit run app.py
```

### Streamlit Community Cloud deployment

Connect the GitHub repo in the Streamlit Cloud dashboard and set `OPENROUTER_API_KEY` in the Secrets section. The app auto-builds the vector store on first launch (takes 60 to 90 seconds). No other configuration needed.

### Run retrieval evaluation

```bash
python -m src.evaluation
```

### Run RAGAS answer-quality evaluation

```bash
python -m src.ragas_evaluation
```

### Run tests

```bash
python -m pytest tests/ -v
```

---

## What I would add with more time

**SqliteSaver for persistent memory.** Swapping MemorySaver for SqliteSaver is a one-line code change that would make conversations persist across page reloads. For someone using the app across multiple job applications over several days, that would be the most noticeable practical improvement.

**Per-tool metadata allowlists.** The retriever currently uses a blocklist to exclude test data. A more precise approach would be per-tool allowlists: interview prep retrieval searches only case study files; skills questions search only the skills inventory. This would sharpen precision without touching the embedding model or chunk size.
