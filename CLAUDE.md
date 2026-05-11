# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CareerFit RAG Coach** is a Turing College Sprint 2 LLM application. It is an AI-powered career coaching tool that analyzes job descriptions against a candidate's profile and returns fit analysis, application positioning, and interview preparation — grounded by a structured knowledge base via RAG.

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** OpenRouter (chat completions)
- **RAG framework:** LangChain
- **Vector store:** ChromaDB
- **Embeddings:** Local sentence-transformers (no API calls for embedding)
- **Language:** Python

## Development Rules

- **Build in phases. Never add features not explicitly requested in the current phase.** Wait for the next phase to be described before implementing it.
- **Keep all code simple and explainable.** This project will be reviewed by a beginner/intermediate developer. Avoid abstractions that obscure what the code is doing.
- **After building each file, run its `if __name__ == "__main__":` test block if one exists.** Do not move to the next file until the current one passes.
- **Always explain what you built before moving to the next file.** Summarize what the file does and why, in plain language.
- **Never invent career claims or personal data.** All output must be grounded in retrieved knowledge base content. If the knowledge base does not support a claim, do not make it.

## Gitignore Requirements

These must always be gitignored — never commit their contents:

- `knowledge_base_private/` — real candidate data
- `vectorstore_demo/` — built from demo knowledge base
- `vectorstore_private/` — built from private knowledge base
- `.env` — API keys (OpenRouter key, etc.)

## Knowledge Base Architecture

The `knowledge_base_demo/` directory is the RAG data source for the demo candidate profile:

| File | Role in RAG |
|------|-------------|
| `cv_summary.md` | Work history, domain expertise — primary retrieval target for fit analysis |
| `skills_inventory.md` | Skill matrix with honest self-assessments — used for gap analysis |
| `education.md` | Degrees, certifications, ongoing learning |
| `career_goals.md` | Target roles, geography, salary, what the candidate is NOT targeting |
| `career_principles.md` | Organising logic behind career decisions — used for motivational framing |
| `application_examples.md` | Tone guidelines and positioning templates — used for output style grounding |
| `hike_case_study.md` | AI education lead role at HIKE — 120+ participants, €1.2M funding |
| `giz_case_study.md` | GIZ internship, LMS redesign, 30% engagement lift |
| `ai_interview_app_case_study.md` | Sprint 1 app, external security review, live URL |
| `ctrl_alt_deity_case_study.md` | AI short film selected for Artefact AI Film Festival Paris 2025 |
| `farout_case_study.md` | NASA data visualisation app built for Replit Buildathon |

`example_job_descriptions.md` lives in `evaluation/` only — it is never embedded into the vector store. `knowledge_base_private/` mirrors the same structure but contains real (non-demo) candidate data and is gitignored.


## Application Flow

```
Input: Job Description (user-provided via Streamlit)
    ↓
RAG Retrieval: ChromaDB + sentence-transformers search over knowledge_base/
    ↓
LangChain + OpenRouter: Synthesize fit analysis with retrieved context
    ↓
Output (displayed in Streamlit):
  - Job fit summary
  - Strengths to emphasize (evidence-backed)
  - Honest gap acknowledgment
  - Tailored talking points / interview prep
```

## Design Constraints

- **Gap honesty is a first-class requirement.** The system must surface and acknowledge skill gaps rather than paper over them. This is a documented principle in `career_goals.md` and `application_examples.md`.
- **Salary floor:** If generating cover letters or negotiation content, never output a single figure — always a range. Floor is €55,000.
