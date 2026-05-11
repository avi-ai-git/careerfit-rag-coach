# CareerFit RAG Coach: Architecture

Sprint 2, LLM Application Development

---

## Overview

CareerFit RAG Coach is a single-user Streamlit app that grounds every answer in a structured knowledge base of the candidate's documented experience. The core constraint is honesty: the system cannot invent achievements, and it must surface gaps explicitly rather than papering over them.

The architecture has six layers that data flows through top to bottom on every request. Each layer has one responsibility and hands off to the next.

```
User input (Streamlit UI)
    |
Security and rate limiting (security.py, app.py)
    |
LangGraph ReAct agent (agent.py)
    |
RAG pipeline: query translation, retrieval, prompt assembly
(query_translation.py, retriever.py, prompts.py)
    |
LLM call (llm.py, OpenRouter or Ollama)
    |
Response rendered in Streamlit with citations and cost estimate
```

---

## Module responsibilities

| Module | Layer | What it does |
|--------|-------|--------------|
| `app.py` | UI | Streamlit page config, sidebar controls, input form, session state, conversation history, export |
| `config.py` | Foundation | Loads `.env`, defines all path constants, chunk size, retrieval k, model defaults |
| `security.py` | Validation | Four-layer input sanitisation: length check, Mistral Moderation (optional), LLM semantic moderation, phrase list |
| `agent.py` | Agent | Wires LLM, tools, and MemorySaver into a LangGraph ReAct agent; runs one turn |
| `tools.py` | Agent | Four career tools and two optional external tools; `_search_impl()` is the shared retrieval core |
| `prompts.py` | Agent | SYSTEM_PROMPT, JOB_FIT_PROMPT, APPLICATION_POSITIONING_PROMPT, INTERVIEW_PREP_PROMPT |
| `query_translation.py` | RAG | Sends user input to LLM, returns 3 to 5 retrieval-optimized phrases |
| `retriever.py` | RAG | Runs ChromaDB similarity search per phrase, merges and deduplicates results |
| `llm.py` | LLM | Returns a `ChatOpenAI` client pointed at OpenRouter or Ollama Cloud based on a set-based model name lookup |
| `vector_store.py` | Data | Builds and loads the ChromaDB vector store from chunked documents |
| `chunker.py` | Data | Splits LangChain Documents into 700-char chunks with 100-char overlap |
| `document_loader.py` | Data | Reads `.md` files from `knowledge_base_demo/`, tags each with `doc_type` metadata |
| `mcp_tools.py` | External | `search_company()` via DuckDuckGo and `search_jobs()` via Adzuna, both opt-in via sidebar |
| `cost_tracking.py` | Support | Token count estimate via tiktoken; per-model pricing lookup; displayed after each reply |
| `logger.py` | Support | Named logger factory; stdout handler; duplicate-handler guard for Streamlit reruns |
| `utils.py` | Support | `truncate_text()` and `format_sources()`, shared display helpers |
| `evaluation.py` | Evaluation | Source-hit check: runs 10 test questions, verifies expected files appear in retrieval results |
| `ragas_evaluation.py` | Evaluation | Answer-quality scoring across four RAGAS metrics |

---

## The four modes and how they differ

The sidebar radio button selects a mode. Each mode changes two things: the input widget type and the prompt prefix that wraps the user's text before it reaches the agent.

| Mode | Input widget | Prompt prefix | Tool the agent calls |
|------|-------------|---------------|----------------------|
| Ask Career Base | `st.text_input` | none (input unchanged) | `search_career_evidence` |
| Analyze Job Fit | `st.text_area` | "Analyze my fit for this job description..." | `analyze_job_fit` |
| Application Positioning | `st.text_area` | "Generate application positioning content..." | `generate_application_positioning` |
| Interview Prep | `st.text_area` | "Prepare interview questions and STAR-style answer notes..." | `generate_interview_prep` |

The prompt prefix is what steers the LangGraph agent toward the right tool. The agent reads the SYSTEM_PROMPT rules plus the prefixed message and selects the appropriate tool. This works because each tool's docstring is specific enough that the agent doesn't need additional routing logic.

---

## The RAG pipeline in detail

Every tool call passes through `_search_impl()` in `tools.py`. This function is the heart of the RAG layer.

### Step 1: query translation (`query_translation.py`)

The raw user input is sent to `translate_query()`, which calls the LLM at temperature 0.3 and asks it to produce 3 to 5 retrieval-optimized phrases. Temperature is slightly higher than the 0.2 used for career output to generate more varied phrases, because diversity across queries improves recall.

The LLM is used here because embedding similarity is sensitive to vocabulary. A user asking "what's my strongest angle for a creative tech role?" retrieves different chunks than "AI film production, generative media, Midjourney" even though they mean the same thing in context. The translation step bridges that gap.

On any failure, the function falls back to `[user_input]`, so the pipeline degrades to single-query retrieval rather than breaking entirely.

The `model` parameter accepts the user's sidebar selection so the query expansion step uses the same model as the rest of the pipeline, rather than always defaulting to `DEFAULT_MODEL`.

### Step 2: multi-query retrieval (`retriever.py`)

Each translated phrase runs as a separate ChromaDB `similarity_search_with_relevance_scores()` call with `k=7`. Results for all phrases are merged and deduplicated by the first 100 characters of each chunk's content.

The vector store is loaded once into a module-level variable (`_vector_store`) rather than reloaded on every call. This eliminates roughly 200ms of reload latency per request.

Results are returned as dicts with keys `content`, `source`, `doc_type`, and `score`. The `source` field is the filename (e.g. `hike_case_study.md`), which is what the LLM cites in its output.

### Step 3: doc type filtering

The three JD-facing tools pass `exclude_doc_types=["test_job_descriptions"]` to the retriever. Without this filter, the `example_job_descriptions.md` evaluation file (22 KB with broad vocabulary across many role types) acts as a retrieval sponge, and its chunks appear in the top results ahead of genuine career evidence files. This is a post-retrieval filter: chunks are retrieved normally and then excluded by metadata tag before being passed to the LLM.

`search_career_evidence` does not apply this filter, because a freeform question should be able to retrieve from the full knowledge base.

### Step 4: prompt assembly (`prompts.py`)

Retrieved chunks are formatted into a labeled context block:

```
--- FILE: hike_case_study.md (case_study) ---
[chunk content]

--- FILE: cv_summary.md (cv_summary) ---
[chunk content]
```

This block is injected into the appropriate structured prompt template as `{context}`. Each template specifies a fixed markdown output format. The fit analysis template, for example, mandates an explicit `## Gaps and Honest Limitations` section. The LLM cannot produce a valid response without completing it. This is how gap honesty is enforced structurally rather than left as a suggestion.

### Step 5: LLM call (`llm.py`)

`get_llm()` returns a `ChatOpenAI` client. Routing uses a set-based lookup:

- Models in `_OLLAMA_CLOUD_MODELS` (`gpt-oss:120b`, `gpt-oss:20b`, `gemma3:27b`) point the client at `OLLAMA_BASE_URL` with `OLLAMA_API_KEY`
- Everything else uses the OpenRouter base URL (`https://openrouter.ai/api/v1`)

Both use the same `ChatOpenAI` class because OpenRouter and Ollama Cloud both implement the OpenAI `/chat/completions` API. Temperature is fixed at 0.2 for consistent, repeatable output.

---

## The LangGraph agent

`create_react_agent()` from `langgraph.prebuilt` wires together the LLM, tool list, MemorySaver, and SYSTEM_PROMPT into a compiled agent graph. LangGraph's ReAct loop runs as follows per turn:

1. LLM receives the user message plus SYSTEM_PROMPT
2. LLM selects a tool and constructs its arguments
3. Tool executes (RAG retrieval and LLM generation happen inside the tool)
4. LLM receives the tool result
5. LLM either calls another tool or writes the final response

The MemorySaver is passed in from `st.session_state` rather than created inside `agent.py`. Without this, each `run_agent()` call would get a fresh MemorySaver and lose all previous turns. Using the same MemorySaver object and the same `thread_id` (a UUID created at session start) gives the agent persistent multi-turn memory within a browser session.

`set_active_model()` is called before each `agent.invoke()` to write the user's sidebar model selection into the `_active_model` module-level variable in `tools.py`. Every subsequent tool call and `translate_query()` call in that turn uses that model.

---

## Security layers

Input is validated before it reaches the agent, in this order:

1. **Length check:** hard block if under 20 or over 15,000 characters. No API call.
2. **Mistral Moderation** (`MISTRAL_API_KEY` optional): hard block. Multilingual semantic detection via Mistral's moderation API. Falls back silently if unreachable.
3. **LLM semantic check:** calls `gpt-4o-mini` via OpenRouter with a SAFE/UNSAFE classifier prompt. Roughly $0.00001 per check. Hard blocks on UNSAFE. Falls back silently on any error.
4. **Phrase list:** soft warning only. 24 known injection patterns. Soft warning because phrase lists are easily bypassed and false positives on legitimate job descriptions are unacceptable.

---

## Optional external tools (`mcp_tools.py`)

Two tools are disabled by default and toggled on in the sidebar:

**`company_research`** calls DuckDuckGo's Instant Answer API. No API key required. The SYSTEM_PROMPT tells the agent to call this first whenever a company name appears in the input. Works well for large global companies; sparse for most regional European companies. Falls back gracefully with a plain text message.

**`find_job_listings`** calls the Adzuna Jobs API. Requires `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`. Only available in Ask Career Base mode — in the three JD modes the user already has a job description and live job search adds confusion rather than value.

---

## Data layer

### Document loading (`document_loader.py`)

Reads all `.md` files from `knowledge_base_demo/` alphabetically. Each file becomes a LangChain `Document` with three metadata fields:

- `source`: filename (e.g. `hike_case_study.md`). Used as the citation label in LLM output.
- `path`: absolute path string.
- `doc_type`: from a hardcoded `_DOC_TYPE_MAP`. Used for retrieval filtering.

### Chunking (`chunker.py`)

`RecursiveCharacterTextSplitter` with `chunk_size=700`, `chunk_overlap=100`. Splits at paragraph breaks first, then sentence boundaries, then word boundaries, so no chunk cuts mid-sentence. The 100-character overlap ensures key phrases near boundaries appear in both adjacent chunks. Each chunk carries its parent document's metadata plus `chunk_index` and `chunk_size_chars`.

11 files produce 144 chunks total.

### Embedding and storage (`vector_store.py`)

`HuggingFaceEmbeddings` loads `all-MiniLM-L6-v2` locally (roughly 90 MB, cached after first download). Each chunk is embedded into a 384-dimensional vector. Vectors and metadata are persisted to `vectorstore_demo/` via ChromaDB. `build_vector_store()` deletes and recreates the persist directory on every call to prevent duplicate embeddings from accumulating across rebuilds.

`app.py` calls `build_vector_store()` automatically on first launch if `vectorstore_demo/` does not exist.

---

## Evaluation

### Retrieval source hits (layer 1)

For each of 10 test questions in `evaluation/test_questions.json`:

1. Retrieve chunks with `exclude_doc_types=["test_job_descriptions"]`
2. Compare retrieved filenames against `expected_sources` in the JSON
3. Record `source_hit` (all expected sources found?) and `score` (fraction found)

Results written to `evaluation/manual_eval_results.csv`. Target: 90% hit rate or above.

### Answer quality with RAGAS (layer 2)

For the same 10 questions, runs the full pipeline (query translation, retrieval, and LLM answer generation) and scores output with RAGAS:

- **Faithfulness:** does the answer only use facts from retrieved context?
- **Answer relevancy:** does the answer address what was asked?
- **Context precision:** are retrieved chunks relevant to the question?
- **Context recall:** did retrieval surface enough to answer correctly?

RAGAS is configured with `LangchainLLMWrapper` and `LangchainEmbeddingsWrapper` so it uses the project's own OpenRouter LLM and local HuggingFace embeddings, with no additional API keys or model downloads required. Results written to `evaluation/ragas_results.csv`.

---

## Key design decisions and their rationale

**ReAct agent over a static chain.** A static chain runs a fixed sequence of steps. The ReAct agent decides at runtime whether to call `company_research` first, then `analyze_job_fit`, based on the user's message. This flexibility also enables multi-turn memory, so the agent can reference earlier turns in the same session.

**Local embeddings over OpenAI's embedding API.** Eliminates a second API dependency, removes per-query embedding cost, and keeps the app functional offline after first download. The tradeoff is lower embedding quality than `text-embedding-3-large`, which is acceptable for an 11-file knowledge base.

**ChromaDB over a managed vector database.** At 144 chunks, a managed service (Pinecone, Weaviate) would add operational complexity (accounts, API keys, network dependency) with no retrieval benefit. ChromaDB runs in-process with disk persistence.

**k=7 over k=5.** After adding four new case study files, the larger knowledge base produced more chunks competing for retrieval slots. At k=5, `hike_case_study.md` was occasionally displaced by more general-vocabulary files. k=7 gives enough slots for relevant content from a larger corpus.

**700-character chunks.** Large enough to include a complete proof point (claim plus outcome) while staying focused enough for high retrieval precision. Larger chunks reduce precision; smaller chunks lose context coherence.

**Gap honesty enforced structurally.** The `## Gaps and Honest Limitations` section is a mandatory part of the fit analysis prompt template. The LLM cannot produce a valid-format response without completing it. This is a structural constraint on the output format, not a prompt suggestion that can be quietly ignored.
